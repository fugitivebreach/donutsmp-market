import discord
from discord.ext import commands
import asyncio
import json
import os
from datetime import datetime, timezone
import os
import asyncio
import discord
from discord.ext import commands
import dotenv

# Load environment variables from parent directory
dotenv.load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '..', 'config', '.env'))

# Bot configuration from environment variables
BOT_TOKEN = os.getenv('BOT_TOKEN', 'YOUR_BOT_TOKEN_HERE')
GUILD_ID = int(os.getenv('GUILD_ID', '123456789012345678'))
TICKET_CATEGORY_ID = int(os.getenv('TICKET_CATEGORY_ID', '123456789012345678'))
SERVER_OWNER_ID = int(os.getenv('SERVER_OWNER_ID', '123456789012345678'))

# Parse comma-separated user and role IDs
ALLOWED_USER_IDS = []
if os.getenv('ALLOWED_USER_IDS'):
    ALLOWED_USER_IDS = [int(uid.strip()) for uid in os.getenv('ALLOWED_USER_IDS').split(',') if uid.strip()]

ALLOWED_ROLE_IDS = []
if os.getenv('ALLOWED_ROLE_IDS'):
    ALLOWED_ROLE_IDS = [int(rid.strip()) for rid in os.getenv('ALLOWED_ROLE_IDS').split(',') if rid.strip()]

# Discord OAuth configuration (for reference)
DISCORD_CLIENT_ID = os.getenv('DISCORD_CLIENT_ID', 'your_discord_client_id_here')
DISCORD_CLIENT_SECRET = os.getenv('DISCORD_CLIENT_SECRET', 'your_discord_client_secret_here')
DISCORD_REDIRECT_URI = os.getenv('DISCORD_REDIRECT_URI', 'http://localhost:3000/auth/callback')

# Bot setup
intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.members = True

bot = commands.Bot(command_prefix='!', intents=intents)

class TicketView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label='Close Ticket', style=discord.ButtonStyle.danger, emoji='🔒')
    async def close_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        # Check if user has permission to close ticket
        if not await has_ticket_permissions(interaction.user, interaction.guild):
            await interaction.response.send_message("❌ You don't have permission to close this ticket.", ephemeral=True)
            return

        # Create confirmation embed
        embed = discord.Embed(
            title="🔒 Close Ticket",
            description="Are you sure you want to close this ticket? This action cannot be undone.",
            color=discord.Color.red()
        )
        
        # Create confirmation view
        confirm_view = ConfirmCloseView()
        await interaction.response.send_message(embed=embed, view=confirm_view, ephemeral=True)

class ConfirmCloseView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=60)

    @discord.ui.button(label='Confirm Close', style=discord.ButtonStyle.danger, emoji='✅')
    async def confirm_close(self, interaction: discord.Interaction, button: discord.ui.Button):
        channel = interaction.channel
        
        # Send closing message
        embed = discord.Embed(
            title="🔒 Ticket Closing",
            description=f"This ticket is being closed by {interaction.user.mention}",
            color=discord.Color.red(),
            timestamp=datetime.now(timezone.utc)
        )
        
        await interaction.response.send_message(embed=embed)
        
        # Wait a moment then delete the channel
        await asyncio.sleep(3)
        await channel.delete(reason=f"Ticket closed by {interaction.user}")

    @discord.ui.button(label='Cancel', style=discord.ButtonStyle.secondary, emoji='❌')
    async def cancel_close(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("❌ Ticket closure cancelled.", ephemeral=True)

async def has_ticket_permissions(user: discord.Member, guild: discord.Guild) -> bool:
    """Check if user has permission to access tickets"""
    # Check if user is server owner
    if user.id == guild.owner_id or user.id == SERVER_OWNER_ID:
        return True
    
    # Check if user ID is in allowed list
    if user.id in ALLOWED_USER_IDS:
        return True
    
    # Check if user has any allowed roles
    user_role_ids = [role.id for role in user.roles]
    if any(role_id in ALLOWED_ROLE_IDS for role_id in user_role_ids):
        return True
    
    return False

class TicketsPanelView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
    
    @discord.ui.button(label="Claim Rewards", style=discord.ButtonStyle.gray, emoji="🎁")
    async def claim_rewards(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Handle claim rewards button click"""
        
        guild = interaction.guild
        category = guild.get_channel(TICKET_CATEGORY_ID)
        
        if not category:
            await interaction.response.send_message("❌ Ticket category not found. Please contact an administrator.", ephemeral=True)
            return
        
        # Check if user already has an open ticket
        existing_ticket = None
        for channel in category.channels:
            if channel.name.startswith(f"rewards-{interaction.user.name.lower()}"):
                existing_ticket = channel
                break
        
        if existing_ticket:
            await interaction.response.send_message(f"❌ You already have an open ticket: {existing_ticket.mention}", ephemeral=True)
            return
        
        try:
            # Create ticket channel
            channel_name = f"rewards-{interaction.user.name.lower()}-{datetime.now().strftime('%m%d%H%M')}"
            
            overwrites = {
                guild.default_role: discord.PermissionOverwrite(read_messages=False),
                guild.me: discord.PermissionOverwrite(read_messages=True, send_messages=True),
                interaction.user: discord.PermissionOverwrite(read_messages=True, send_messages=True)
            }
            
            # Add staff permissions
            for role_id in ALLOWED_ROLE_IDS:
                role = guild.get_role(role_id)
                if role:
                    overwrites[role] = discord.PermissionOverwrite(read_messages=True, send_messages=True)
            
            channel = await category.create_text_channel(
                name=channel_name,
                overwrites=overwrites
            )
            
            # Create welcome embed
            embed = discord.Embed(
                title="🎁 Claim Rewards Ticket",
                description=f"Hello {interaction.user.mention}! Welcome to your rewards ticket.",
                color=0x4caf50,
                timestamp=datetime.now(timezone.utc)
            )
            
            embed.add_field(
                name="📋 What to include:",
                value="• Your Discord username\n• What rewards you're claiming\n• Any relevant screenshots or proof\n• Transaction IDs if applicable",
                inline=False
            )
            
            embed.add_field(
                name="⏰ Next Steps:",
                value="A staff member will review your request and assist you shortly.",
                inline=False
            )
            
            embed.set_footer(text="DonutMarket Support", icon_url="https://donutmarket.store/static/logo1.png")
            
            # Add close button
            close_view = CloseTicketView()
            
            await channel.send(f"🎫 **Ticket Created**\n{interaction.user.mention}", embed=embed, view=close_view)
            
            await interaction.response.send_message(f"✅ Your rewards ticket has been created: {channel.mention}", ephemeral=True)
            
        except discord.Forbidden:
            await interaction.response.send_message("❌ I don't have permission to create channels.", ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"❌ Error creating ticket: {str(e)}", ephemeral=True)

class CloseTicketView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
    
    @discord.ui.button(label="Close Ticket", style=discord.ButtonStyle.red, emoji="🔒")
    async def close_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Handle close ticket button"""
        
        # Check if user has permission to close
        if not await has_ticket_permissions(interaction.user, interaction.guild):
            await interaction.response.send_message("❌ You don't have permission to close tickets.", ephemeral=True)
            return
        
        embed = discord.Embed(
            title="🔒 Ticket Closed",
            description=f"This ticket has been closed by {interaction.user.mention}",
            color=0xff0000,
            timestamp=datetime.now(timezone.utc)
        )
        
        await interaction.response.send_message(embed=embed)
        
        # Delete channel after 5 seconds
        await asyncio.sleep(5)
        await interaction.followup.channel.delete()

@bot.event
async def on_ready():
    print(f"✅ {bot.user} has connected to Discord!")
    print(f"📊 Bot is in {len(bot.guilds)} guilds")
    
    # Add persistent views for buttons to work after restart
    bot.add_view(TicketsPanelView())
    bot.add_view(CloseTicketView())
    
    # Sync slash commands
    try:
        synced = await bot.tree.sync()
        print(f'✅ Synced {len(synced)} slash command(s)')
        for cmd in synced:
            print(f'   - /{cmd.name}')
    except Exception as e:
        print(f'❌ Failed to sync commands: {e}')
    
    # List all guilds the bot is in
    print(f"🔍 Available guilds:")
    for g in bot.guilds:
        print(f"   - {g.name} (ID: {g.id})")
    
    # Check if we can find the target guild
    guild = bot.get_guild(GUILD_ID)
    if guild:
        print(f"🏠 Connected to guild: {guild.name}")
        category = discord.utils.get(guild.categories, id=TICKET_CATEGORY_ID)
        if category:
            print(f"📁 Ticket category found: {category.name}")
        else:
            print(f"❌ Ticket category not found (ID: {TICKET_CATEGORY_ID})")
            print(f"🔍 Available categories in {guild.name}:")
    
    # Sync slash commands
    try:
        synced = await bot.tree.sync()
        print(f'✅ Synced {len(synced)} command(s)')
    except Exception as e:
        print(f'❌ Failed to sync commands: {e}')
    
    print('🎫 DonutMarket Bot is ready for ticket management!')

@bot.tree.command(name="create_ticket", description="Create a new support ticket")
async def create_ticket_command(interaction: discord.Interaction, reason: str = "General Support"):
    """Manual ticket creation command"""
    if not await has_ticket_permissions(interaction.user, interaction.guild):
        await interaction.response.send_message("❌ You don't have permission to create tickets.", ephemeral=True)
        return
    
    guild = interaction.guild
    category = discord.utils.get(guild.categories, id=TICKET_CATEGORY_ID)
    
    if not category:
        await interaction.response.send_message("❌ Ticket category not found. Please contact an administrator.", ephemeral=True)
        return
    
    # Create ticket channel
    channel_name = f"ticket-{interaction.user.name}-{datetime.now().strftime('%m%d%H%M')}"
    
    # Set permissions for the ticket channel
    overwrites = {
        guild.default_role: discord.PermissionOverwrite(read_messages=False),
        interaction.user: discord.PermissionOverwrite(read_messages=True, send_messages=True),
        guild.me: discord.PermissionOverwrite(read_messages=True, send_messages=True)
    }
    
    # Add permissions for allowed users and roles
    for user_id in ALLOWED_USER_IDS:
        user = guild.get_member(user_id)
        if user:
            overwrites[user] = discord.PermissionOverwrite(read_messages=True, send_messages=True)
    
    for role_id in ALLOWED_ROLE_IDS:
        role = guild.get_role(role_id)
        if role:
            overwrites[role] = discord.PermissionOverwrite(read_messages=True, send_messages=True)
    
    # Create the channel
    ticket_channel = await guild.create_text_channel(
        name=channel_name,
        category=category,
        overwrites=overwrites,
        reason=f"Support ticket created by {interaction.user}"
    )
    
    # Create ticket embed
    embed = discord.Embed(
        title="🎫 Support Ticket Created",
        description=f"**Reason:** {reason}\n**Created by:** {interaction.user.mention}",
        color=discord.Color.blue(),
        timestamp=datetime.now(timezone.utc)
    )
    embed.add_field(name="📋 Instructions", value="Please describe your issue in detail. A staff member will assist you shortly.", inline=False)
    embed.set_footer(text=f"Ticket ID: {ticket_channel.id}")
    
    # Send ticket message with close button
    view = TicketView()
    await ticket_channel.send(embed=embed, view=view)
    
    # Respond to the interaction
    await interaction.response.send_message(f"✅ Ticket created: {ticket_channel.mention}", ephemeral=True)

async def create_purchase_ticket(buyer_name, discord_user, transaction_id, total_amount, items):
    """Create a ticket for a store purchase"""
    guild = bot.get_guild(GUILD_ID)
    if not guild:
        print(f"❌ Guild with ID {GUILD_ID} not found")
        print(f"🔍 Available guilds:")
        for g in bot.guilds:
            print(f"   - {g.name} (ID: {g.id})")
        print(f"💡 Make sure the bot is invited to the correct server and has proper permissions")
        return None
    
    category = discord.utils.get(guild.categories, id=TICKET_CATEGORY_ID)
    if not category:
        print(f"Category with ID {TICKET_CATEGORY_ID} not found")
        return None
    
    # Create ticket channel name
    channel_name = f"purchase-{buyer_name.lower().replace('#', '')}-{datetime.now().strftime('%m%d%H%M')}"
    
    # Set permissions for the ticket channel
    overwrites = {
        guild.default_role: discord.PermissionOverwrite(read_messages=False),
        guild.me: discord.PermissionOverwrite(read_messages=True, send_messages=True)
    }
    
    # Try to find the buyer in the guild
    buyer_member = None
    for member in guild.members:
        if str(member) == discord_user or member.display_name.lower() == buyer_name.lower():
            buyer_member = member
            break
    
    if buyer_member:
        overwrites[buyer_member] = discord.PermissionOverwrite(read_messages=True, send_messages=True)
    
    # Add permissions for allowed users and roles
    for user_id in ALLOWED_USER_IDS:
        user = guild.get_member(user_id)
        if user:
            overwrites[user] = discord.PermissionOverwrite(read_messages=True, send_messages=True)
    
    for role_id in ALLOWED_ROLE_IDS:
        role = guild.get_role(role_id)
        if role:
            overwrites[role] = discord.PermissionOverwrite(read_messages=True, send_messages=True)
    
    try:
        # Create the channel
        ticket_channel = await guild.create_text_channel(
            name=channel_name,
            category=category,
            overwrites=overwrites,
            reason=f"Store purchase ticket for {buyer_name}"
        )
        
        # Create purchase embed with proper formatting
        embed = discord.Embed(
            title="🛒 New Store Purchase",
            description="A new purchase has been made on DonutMarket!",
            color=discord.Color.dark_blue(),
            timestamp=datetime.now(timezone.utc)
        )
        
        # Add buyer information
        embed.add_field(name="👤 Buyer", value=f"`{buyer_name}`", inline=True)
        embed.add_field(name="💬 Discord", value=f"`{discord_user}`", inline=True)
        embed.add_field(name="🆔 Transaction ID", value=f"`{transaction_id}`", inline=True)
        embed.add_field(name="💰 Total Amount", value=f"**${total_amount}**", inline=True)
        
        # Add purchased items with better formatting
        items_text = ""
        for item in items:
            amount = item.get('amount', '1x')
            name = item.get('name', 'Unknown Item')
            items_text += f"• **{amount}** {name}\n"
        
        if items_text:
            embed.add_field(name="📦 Purchased Items", value=items_text, inline=False)
        else:
            embed.add_field(name="📦 Purchased Items", value="No items listed", inline=False)
        
        # Add store owner mention
        server_owner = guild.get_member(SERVER_OWNER_ID)
        if server_owner:
            embed.add_field(name="🏪 Store Owner", value=server_owner.mention, inline=False)
        
        # Add instructions
        embed.add_field(
            name="📋 Next Steps", 
            value="✅ Verify the purchase details\n✅ Process the delivery\n✅ Close ticket when complete", 
            inline=False
        )
        
        embed.set_footer(text=f"Ticket ID: {ticket_channel.id} | DonutMarket Store")
        embed.set_thumbnail(url="https://donutmarket.store/static/logo1.png")
        
        # Send welcome message first
        welcome_msg = f"🎫 **Purchase Ticket Created**\n\n"
        welcome_msg += f"Hello {buyer_member.mention if buyer_member else buyer_name}! "
        welcome_msg += f"Your purchase ticket has been created.\n\n"
        welcome_msg += f"**Order Details:**\n"
        welcome_msg += f"• Transaction: `{transaction_id}`\n"
        welcome_msg += f"• Amount: **${total_amount}**\n\n"
        welcome_msg += f"Our team will process your order shortly. Please wait for delivery confirmation."
        
        await ticket_channel.send(welcome_msg)
        
        # Send the detailed embed with close button
        view = TicketView()
        message = await ticket_channel.send(embed=embed, view=view)
        
        # Pin the detailed message
        await message.pin()
        
        print(f"Purchase ticket created: {ticket_channel.name}")
        return ticket_channel
        
    except Exception as e:
        print(f"Error creating purchase ticket: {e}")
        return None

@bot.tree.command(name="test_purchase", description="Test the purchase ticket system")
async def test_purchase_command(interaction: discord.Interaction):
    """Test command for purchase tickets"""
    if not await has_ticket_permissions(interaction.user, interaction.guild):
        await interaction.response.send_message("❌ You don't have permission to use this command.", ephemeral=True)
        return
    
    # Test data
    test_items = [
        {"name": "DonutSMP Money", "amount": "200M"},
        {"name": "Netherite Armor", "amount": "1x"}
    ]
    
    await interaction.response.defer()
    
    ticket_channel = await create_purchase_ticket(
        buyer_name="TestUser",
        discord_user="TestUser#1234",
        transaction_id="TEST_12345",
        total_amount="25.00",
        items=test_items
    )
    
    
    # Check if this is a ticket channel
    if not (channel.name.startswith('ticket-') or channel.name.startswith('purchase-')):
        await interaction.response.send_message("❌ This command can only be used in ticket channels.", ephemeral=True)
        return
    
    # Create confirmation embed
    embed = discord.Embed(
        title="🔒 Close Ticket",
        description="Are you sure you want to close this ticket? This action cannot be undone.",
        color=discord.Color.red()
    )
    
    # Create confirmation view
    confirm_view = ConfirmCloseView()
    await interaction.response.send_message(embed=embed, view=confirm_view, ephemeral=True)

@bot.tree.command(name="bot_info", description="Show bot information and configuration")
async def bot_info_command(interaction: discord.Interaction):
    """Show bot information"""
    if not await has_ticket_permissions(interaction.user, interaction.guild):
        await interaction.response.send_message("❌ You don't have permission to use this command.", ephemeral=True)
        return
    
    guild = bot.get_guild(GUILD_ID)
    category = discord.utils.get(guild.categories, id=TICKET_CATEGORY_ID) if guild else None
    
    embed = discord.Embed(
        title="🤖 DonutMarket Bot Information",
        color=discord.Color.blue(),
        timestamp=datetime.now(timezone.utc)
    )
    
    embed.add_field(name="📊 Bot Status", value=f"✅ Online\n🏠 Guild: {guild.name if guild else 'Not Found'}", inline=True)
    embed.add_field(name="🎫 Ticket System", value=f"📁 Category: {category.name if category else 'Not Found'}\n🔧 Status: {'Ready' if category else 'Error'}", inline=True)
    embed.add_field(name="👥 Permissions", value=f"👤 Allowed Users: {len(ALLOWED_USER_IDS)}\n🎭 Allowed Roles: {len(ALLOWED_ROLE_IDS)}", inline=True)
    
    # Count open tickets
    open_tickets = 0
    if guild and category:
        for channel in category.channels:
            if channel.name.startswith(('ticket-', 'purchase-')):
                open_tickets += 1
    
    embed.add_field(name="📈 Statistics", value=f"🎫 Open Tickets: {open_tickets}\n🔗 Webhook: Running on :8080", inline=False)
    
    embed.set_footer(text="DonutMarket Ticket System")
    
    await interaction.response.send_message(embed=embed, ephemeral=False)

@bot.tree.command(name="list_tickets", description="List all open tickets")
async def list_tickets_command(interaction: discord.Interaction):
    """List all open tickets"""
    if not await has_ticket_permissions(interaction.user, interaction.guild):
        await interaction.response.send_message("❌ You don't have permission to use this command.", ephemeral=True)
        return
    
    guild = bot.get_guild(GUILD_ID)
    category = discord.utils.get(guild.categories, id=TICKET_CATEGORY_ID) if guild else None
    
    if not category:
        await interaction.response.send_message("❌ Ticket category not found.", ephemeral=True)
        return
    
    tickets = []
    for channel in category.channels:
        if channel.name.startswith(('ticket-', 'purchase-')):
            # Get creation time
            created = channel.created_at.strftime("%m/%d %H:%M")
            ticket_type = "🛒 Purchase" if channel.name.startswith('purchase-') else "🎫 Support"
            tickets.append(f"{ticket_type} {channel.mention} - Created {created}")
    
    if not tickets:
        embed = discord.Embed(
            title="🎫 Open Tickets",
            description="No open tickets found.",
            color=discord.Color.green()
        )
    else:
        embed = discord.Embed(
            title="🎫 Open Tickets",
            description="\n".join(tickets[:10]),  # Limit to 10 tickets
            color=discord.Color.blue()
        )
        
        if len(tickets) > 10:
            embed.set_footer(text=f"Showing 10 of {len(tickets)} tickets")
    
    await interaction.response.send_message(embed=embed, ephemeral=True)

@bot.tree.command(name="tickets-panel", description="Send a tickets panel to a channel")
async def tickets_panel(interaction: discord.Interaction, channel: discord.TextChannel, message_id: str = None):
    """Send or edit a tickets panel with claim rewards button"""
    
    # Check permissions
    if not await has_ticket_permissions(interaction.user, interaction.guild):
        await interaction.response.send_message("❌ You don't have permission to use this command.", ephemeral=True)
        return
    
    # Create the embed
    embed = discord.Embed(
        title="🎫 Tickets Panel",
        description="Need help or want to claim rewards? Use the button below!",
        color=0x036fff
    )
    
    embed.add_field(
        name="📋 How to use:",
        value="• Click **Claim Rewards** to create a ticket\n• Staff will assist you as soon as possible\n• Only create tickets when needed",
        inline=False
    )
    
    embed.add_field(
        name="⏰ Response Time:",
        value="We typically respond within 1-24 hours",
        inline=True
    )
    
    embed.add_field(
        name="🏪 Store Support:",
        value="For purchase issues, include your transaction ID",
        inline=True
    )
    
    embed.set_footer(text="DonutMarket Support System", icon_url="https://donutmarket.store/static/logo1.png")
    
    # Create the view with claim rewards button
    view = TicketsPanelView()
    
    try:
        if message_id and message_id.lower() != "none":
            # Edit existing message
            try:
                message = await channel.fetch_message(int(message_id))
                await message.edit(embed=embed, view=view)
                await interaction.response.send_message(f"✅ Updated tickets panel in {channel.mention}", ephemeral=True)
            except discord.NotFound:
                await interaction.response.send_message("❌ Message not found. Sending new panel instead.", ephemeral=True)
                message = await channel.send(embed=embed, view=view)
                await interaction.followup.send(f"✅ New tickets panel sent to {channel.mention}\n**Message ID:** `{message.id}`", ephemeral=True)
            except ValueError:
                await interaction.response.send_message("❌ Invalid message ID. Sending new panel instead.", ephemeral=True)
                message = await channel.send(embed=embed, view=view)
                await interaction.followup.send(f"✅ New tickets panel sent to {channel.mention}\n**Message ID:** `{message.id}`", ephemeral=True)
        else:
            # Send new message
            message = await channel.send(embed=embed, view=view)
            await interaction.response.send_message(f"✅ Tickets panel sent to {channel.mention}\n**Message ID:** `{message.id}`", ephemeral=True)
            
    except discord.Forbidden:
        await interaction.response.send_message("❌ I don't have permission to send messages in that channel.", ephemeral=True)
    except Exception as e:
        await interaction.response.send_message(f"❌ Error: {str(e)}", ephemeral=True)

# Web server integration (for receiving purchase webhooks)
try:
    from aiohttp import web
    import aiohttp_cors
    AIOHTTP_AVAILABLE = True
except ImportError:
    print("⚠️  aiohttp/aiohttp-cors not available - webhook server will be disabled")
    AIOHTTP_AVAILABLE = False

if AIOHTTP_AVAILABLE:
    async def handle_purchase_webhook(request):
        """Handle purchase webhook from the website"""
        try:
            print("🔔 Received purchase webhook!")
            data = await request.json()
            print(f"📋 Webhook data: {data}")
            
            # Extract purchase data
            buyer_name = data.get('buyer', 'Unknown')
            discord_user = data.get('discord', 'Unknown')
            transaction_id = data.get('transactionId', 'Unknown')
            total_amount = data.get('totalAmount', '0.00')
            items = data.get('items', [])
            
            print(f"🎫 Creating ticket for {buyer_name} (${total_amount})")
            
            # Create the ticket
            ticket_channel = await create_purchase_ticket(
                buyer_name=buyer_name,
                discord_user=discord_user,
                transaction_id=transaction_id,
                total_amount=total_amount,
                items=items
            )
            
            if ticket_channel:
                print(f"✅ Ticket created successfully: {ticket_channel.name}")
                return web.json_response({
                    'success': True,
                    'ticket_id': ticket_channel.id,
                    'ticket_name': ticket_channel.name
                })
            else:
                print("❌ Failed to create ticket")
                return web.json_response({
                    'success': False,
                    'error': 'Failed to create ticket'
                }, status=500)
                
        except Exception as e:
            print(f"❌ Error handling purchase webhook: {e}")
            import traceback
            traceback.print_exc()
            return web.json_response({
                'success': False,
                'error': str(e)
            }, status=500)

if AIOHTTP_AVAILABLE:
    async def handle_health_check(request):
        """Health check endpoint"""
        guild = bot.get_guild(GUILD_ID)
        category = discord.utils.get(guild.categories, id=TICKET_CATEGORY_ID) if guild else None
        
        return web.json_response({
            'status': 'healthy',
            'bot_connected': bot.is_ready(),
            'guild_connected': guild is not None,
            'category_found': category is not None,
            'timestamp': datetime.now(timezone.utc).isoformat()
        })

async def start_web_server():
    """Start the web server for webhooks"""
    # Skip webhook server in Railway production (Express server handles webhooks)
    if os.getenv('RAILWAY_ENVIRONMENT') == 'production':
        print("🚀 Running in Railway production - webhook server handled by Express")
        return
        
    if not AIOHTTP_AVAILABLE:
        print("⚠️  Webhook server disabled - aiohttp not available")
        return
    
    try:
        app = web.Application()
        
        # Setup CORS
        cors = aiohttp_cors.setup(app, defaults={
            "*": aiohttp_cors.ResourceOptions(
                allow_credentials=True,
                expose_headers="*",
                allow_headers="*",
                allow_methods="*"
            )
        })
        
        # Add routes
        app.router.add_post('/webhook/purchase', handle_purchase_webhook)
        app.router.add_get('/health', handle_health_check)
        
        # Add CORS to all routes
        for route in list(app.router.routes()):
            cors.add(route)
        
        runner = web.AppRunner(app)
        await runner.setup()
        site = web.TCPSite(runner, 'localhost', 8080)
        await site.start()
        print("✅ Webhook server started on http://localhost:8080")
    except Exception as e:
        print(f"❌ Failed to start webhook server: {e}")
        print("🤖 Bot will continue without webhook functionality")

async def process_ticket_files():
    """Process ticket files created by Express server (Railway mode)"""
    if os.getenv('RAILWAY_ENVIRONMENT') != 'production':
        return
        
    tickets_dir = os.path.join(os.path.dirname(__file__), '..', 'tickets')
    if not os.path.exists(tickets_dir):
        return
        
    for filename in os.listdir(tickets_dir):
        if filename.startswith('ticket_') and filename.endswith('.json'):
            file_path = os.path.join(tickets_dir, filename)
            try:
                with open(file_path, 'r') as f:
                    ticket_data = json.load(f)
                
                print(f"🎫 Processing ticket file: {filename}")
                
                # Create Discord ticket
                guild = bot.get_guild(GUILD_ID)
                if guild:
                    category = guild.get_channel(TICKET_CATEGORY_ID)
                    if category:
                        # Create ticket channel
                        channel_name = f"purchase-{ticket_data['buyer'].replace('#', '').replace('.', '').lower()}-{datetime.now().strftime('%m%d%H%M')}"
                        
                        overwrites = {
                            guild.default_role: discord.PermissionOverwrite(read_messages=False),
                            guild.me: discord.PermissionOverwrite(read_messages=True, send_messages=True)
                        }
                        
                        # Add user permissions if they're in the server
                        for member in guild.members:
                            if str(member) == ticket_data['discord']:
                                overwrites[member] = discord.PermissionOverwrite(read_messages=True, send_messages=True)
                                break
                        
                        channel = await category.create_text_channel(
                            name=channel_name,
                            overwrites=overwrites
                        )
                        
                        # Create embed
                        embed = discord.Embed(
                            title="🛒 New Purchase",
                            description=f"Purchase from {ticket_data.get('store', 'DonutMarket')}",
                            color=0x036fff,
                            timestamp=datetime.now(timezone.utc)
                        )
                        
                        embed.add_field(name="👤 Buyer", value=ticket_data['buyer'], inline=True)
                        embed.add_field(name="💰 Total", value=f"${ticket_data['totalAmount']}", inline=True)
                        embed.add_field(name="🆔 Transaction", value=ticket_data['transactionId'], inline=True)
                        
                        items_text = ""
                        for item in ticket_data['items']:
                            items_text += f"• {item['name']} - {item['amount']} (${item['price']})\n"
                        
                        embed.add_field(name="📦 Items", value=items_text, inline=False)
                        embed.add_field(name="🏪 Store", value=ticket_data.get('store', 'DonutMarket'), inline=True)
                        
                        await channel.send(embed=embed)
                        
                        print(f"✅ Created Discord ticket: {channel.name}")
                        
                        # Delete processed file
                        os.remove(file_path)
                        print(f"🗑️ Removed processed ticket file: {filename}")
                        
            except Exception as e:
                print(f"❌ Error processing ticket file {filename}: {e}")

async def ticket_file_watcher():
    """Watch for new ticket files every 5 seconds"""
    while True:
        try:
            await process_ticket_files()
        except Exception as e:
            print(f"❌ Error in ticket file watcher: {e}")
        await asyncio.sleep(5)

async def main():
    """Main function to start both bot and web server"""
    # Start web server (only in local mode)
    await start_web_server()
    
    # Start ticket file watcher (only in Railway mode)
    if os.getenv('RAILWAY_ENVIRONMENT') == 'production':
        print("🎫 Starting ticket file watcher for Railway mode...")
        asyncio.create_task(ticket_file_watcher())
    
    # Start bot
    await bot.start(BOT_TOKEN)

if __name__ == "__main__":
    print("🤖 DonutMarket Discord Bot Starting...")
    print(f"📋 Configuration:")
    print(f"   Guild ID: {GUILD_ID}")
    print(f"   Category ID: {TICKET_CATEGORY_ID}")
    print(f"   Server Owner ID: {SERVER_OWNER_ID}")
    print(f"   Allowed Users: {len(ALLOWED_USER_IDS)} configured")
    print(f"   Railway Environment: {os.getenv('RAILWAY_ENVIRONMENT', 'local')}")
    print(f"   Bot Token: {'SET (' + BOT_TOKEN[:10] + '...)' if BOT_TOKEN and BOT_TOKEN != 'YOUR_BOT_TOKEN_HERE' else 'NOT SET'}")
    
    # Debug all environment variables
    print(f"🔍 Environment Variables:")
    print(f"   BOT_TOKEN: {os.getenv('BOT_TOKEN', 'NOT SET')[:10] if os.getenv('BOT_TOKEN') else 'NOT SET'}...")
    print(f"   DISCORD_BOT_TOKEN: {os.getenv('DISCORD_BOT_TOKEN', 'NOT SET')[:10] if os.getenv('DISCORD_BOT_TOKEN') else 'NOT SET'}...")
    print(f"   GUILD_ID: {os.getenv('GUILD_ID', 'NOT SET')}")
    print(f"   TICKET_CATEGORY_ID: {os.getenv('TICKET_CATEGORY_ID', 'NOT SET')}")
    
    # Check if required environment variables are set
    if BOT_TOKEN == 'YOUR_BOT_TOKEN_HERE' or not BOT_TOKEN:
        print("❌ BOT_TOKEN not configured!")
        print("   Please set the BOT_TOKEN environment variable")
        print("   In Railway: Add BOT_TOKEN to environment variables")
        print("   Locally: Add BOT_TOKEN=your_token to .env file")
        print("   Current BOT_TOKEN value:", repr(BOT_TOKEN))
        print("⚠️  Bot will exit - cannot start without token")
        exit(1)
    
    if GUILD_ID == 123456789012345678:
        print("⚠️  GUILD_ID not configured - using default")
        print("   Please set the GUILD_ID environment variable")
    
    if TICKET_CATEGORY_ID == 123456789012345678:
        print("⚠️  TICKET_CATEGORY_ID not configured - using default")
        print("   Please set the TICKET_CATEGORY_ID environment variable")
    
    print(f"   Allowed Roles: {len(ALLOWED_ROLE_IDS)} configured")
    
    print("\n🚀 Starting bot and webhook server...")
    
    # Run the bot
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Bot stopped by user")
    except Exception as e:
        print(f"\n❌ Bot crashed: {e}")
        import traceback
        traceback.print_exc()
