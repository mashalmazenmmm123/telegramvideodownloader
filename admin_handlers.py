"""
Admin command handlers for the Telegram Video Downloader Bot
Professional admin system with user management and premium features
"""

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, CallbackQueryHandler
from telegram.constants import ParseMode
from datetime import datetime, timedelta
from models import get_db, User, AdminLog, Download
from sqlalchemy.orm import sessionmaker
from sqlalchemy import func
import logging

logger = logging.getLogger(__name__)

# Initial admin user ID - change this to your Telegram user ID
INITIAL_ADMIN_ID = "6827554082"  # Replace with your Telegram user ID

async def is_admin(user_id: str) -> bool:
    """Check if user is admin"""
    db = get_db()
    try:
        user = db.query(User).filter(User.user_id == str(user_id)).first()
        return user and user.is_admin()
    finally:
        db.close()

async def ensure_user_exists(user_id: str, username: str = None, first_name: str = None, last_name: str = None):
    """Ensure user exists in database"""
    db = get_db()
    try:
        user = db.query(User).filter(User.user_id == str(user_id)).first()
        if not user:
            user = User(
                user_id=str(user_id),
                username=username,
                first_name=first_name,
                last_name=last_name,
                user_type='admin' if str(user_id) == INITIAL_ADMIN_ID else 'normal'
            )
            db.add(user)
            db.commit()
            logger.info(f"Created new user: {user_id}")
        else:
            # Update user info
            user.username = username
            user.first_name = first_name
            user.last_name = last_name
            user.last_active = datetime.utcnow()
            db.commit()
        return user
    finally:
        db.close()

async def admin_panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show admin control panel"""
    user_id = str(update.effective_user.id)
    
    if not await is_admin(user_id):
        await update.message.reply_text("❌ Access denied. Admin privileges required.")
        return
    
    keyboard = [
        [InlineKeyboardButton("👥 User Management", callback_data="admin_users")],
        [InlineKeyboardButton("💎 Premium Management", callback_data="admin_premium")],
        [InlineKeyboardButton("📊 Statistics", callback_data="admin_stats")],
        [InlineKeyboardButton("⚙️ Settings", callback_data="admin_settings")],
        [InlineKeyboardButton("📝 Admin Logs", callback_data="admin_logs")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    text = """
🔧 **Admin Control Panel**

Welcome to the admin dashboard. Choose an option below:

👥 **User Management** - Add/remove admins, ban users
💎 **Premium Management** - Grant/revoke premium access
📊 **Statistics** - View bot usage statistics
⚙️ **Settings** - Configure bot settings
📝 **Admin Logs** - View admin action history
"""
    
    await update.message.reply_text(text, reply_markup=reply_markup, parse_mode=ParseMode.MARKDOWN)

async def add_admin_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Add new admin - Usage: /addadmin <user_id>"""
    user_id = str(update.effective_user.id)
    
    if not await is_admin(user_id):
        await update.message.reply_text("❌ Access denied. Admin privileges required.")
        return
    
    if not context.args:
        await update.message.reply_text("Usage: /addadmin <user_id>\nExample: /addadmin 123456789")
        return
    
    target_user_id = context.args[0]
    
    db = get_db()
    try:
        # Check if target user exists
        target_user = db.query(User).filter(User.user_id == target_user_id).first()
        if not target_user:
            await update.message.reply_text(f"❌ User {target_user_id} not found. They need to start the bot first.")
            return
        
        if target_user.is_admin():
            await update.message.reply_text(f"⚠️ User {target_user_id} is already an admin.")
            return
        
        # Grant admin privileges
        target_user.user_type = 'admin'
        db.commit()
        
        # Log admin action
        log_entry = AdminLog(
            admin_user_id=user_id,
            action='add_admin',
            target_user_id=target_user_id,
            details=f"Granted admin privileges to user {target_user_id}"
        )
        db.add(log_entry)
        db.commit()
        
        await update.message.reply_text(f"✅ Successfully granted admin privileges to user {target_user_id}")
        logger.info(f"Admin {user_id} granted admin privileges to {target_user_id}")
        
    finally:
        db.close()

async def grant_premium_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Grant premium access - Usage: /premium <user_id> <days>"""
    user_id = str(update.effective_user.id)
    
    if not await is_admin(user_id):
        await update.message.reply_text("❌ Access denied. Admin privileges required.")
        return
    
    if len(context.args) < 2:
        await update.message.reply_text("Usage: /premium <user_id> <days>\nExample: /premium 123456789 30")
        return
    
    target_user_id = context.args[0]
    try:
        days = int(context.args[1])
    except ValueError:
        await update.message.reply_text("❌ Invalid number of days. Please enter a valid number.")
        return
    
    db = get_db()
    try:
        # Check if target user exists
        target_user = db.query(User).filter(User.user_id == target_user_id).first()
        if not target_user:
            await update.message.reply_text(f"❌ User {target_user_id} not found. They need to start the bot first.")
            return
        
        # Grant premium access
        target_user.user_type = 'premium'
        target_user.premium_until = datetime.utcnow() + timedelta(days=days)
        target_user.added_by_admin = user_id
        db.commit()
        
        # Log admin action
        log_entry = AdminLog(
            admin_user_id=user_id,
            action='grant_premium',
            target_user_id=target_user_id,
            details=f"Granted {days} days of premium access"
        )
        db.add(log_entry)
        db.commit()
        
        await update.message.reply_text(f"✅ Successfully granted {days} days of premium access to user {target_user_id}")
        logger.info(f"Admin {user_id} granted {days} days premium to {target_user_id}")
        
    finally:
        db.close()

async def ban_user_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Ban user - Usage: /ban <user_id>"""
    user_id = str(update.effective_user.id)
    
    if not await is_admin(user_id):
        await update.message.reply_text("❌ Access denied. Admin privileges required.")
        return
    
    if not context.args:
        await update.message.reply_text("Usage: /ban <user_id>\nExample: /ban 123456789")
        return
    
    target_user_id = context.args[0]
    
    db = get_db()
    try:
        target_user = db.query(User).filter(User.user_id == target_user_id).first()
        if not target_user:
            await update.message.reply_text(f"❌ User {target_user_id} not found.")
            return
        
        if target_user.is_admin():
            await update.message.reply_text("❌ Cannot ban admin users.")
            return
        
        target_user.is_banned = True
        db.commit()
        
        # Log admin action
        log_entry = AdminLog(
            admin_user_id=user_id,
            action='ban_user',
            target_user_id=target_user_id,
            details=f"Banned user {target_user_id}"
        )
        db.add(log_entry)
        db.commit()
        
        await update.message.reply_text(f"✅ Successfully banned user {target_user_id}")
        logger.info(f"Admin {user_id} banned user {target_user_id}")
        
    finally:
        db.close()

async def unban_user_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Unban user - Usage: /unban <user_id>"""
    user_id = str(update.effective_user.id)
    
    if not await is_admin(user_id):
        await update.message.reply_text("❌ Access denied. Admin privileges required.")
        return
    
    if not context.args:
        await update.message.reply_text("Usage: /unban <user_id>\nExample: /unban 123456789")
        return
    
    target_user_id = context.args[0]
    
    db = get_db()
    try:
        target_user = db.query(User).filter(User.user_id == target_user_id).first()
        if not target_user:
            await update.message.reply_text(f"❌ User {target_user_id} not found.")
            return
        
        target_user.is_banned = False
        db.commit()
        
        # Log admin action
        log_entry = AdminLog(
            admin_user_id=user_id,
            action='unban_user',
            target_user_id=target_user_id,
            details=f"Unbanned user {target_user_id}"
        )
        db.add(log_entry)
        db.commit()
        
        await update.message.reply_text(f"✅ Successfully unbanned user {target_user_id}")
        logger.info(f"Admin {user_id} unbanned user {target_user_id}")
        
    finally:
        db.close()

async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show bot statistics"""
    user_id = str(update.effective_user.id)
    
    if not await is_admin(user_id):
        await update.message.reply_text("❌ Access denied. Admin privileges required.")
        return
    
    db = get_db()
    try:
        # Get user statistics
        total_users = db.query(User).count()
        premium_users = db.query(User).filter(User.user_type == 'premium').count()
        admin_users = db.query(User).filter(User.user_type == 'admin').count()
        banned_users = db.query(User).filter(User.is_banned == True).count()
        
        # Get download statistics
        total_downloads = db.query(Download).count()
        successful_downloads = db.query(Download).filter(Download.status == 'success').count()
        failed_downloads = db.query(Download).filter(Download.status == 'failed').count()
        
        # Today's statistics
        today = datetime.utcnow().date()
        today_downloads = db.query(Download).filter(func.date(Download.created_at) == today).count()
        today_users = db.query(User).filter(func.date(User.last_active) == today).count()
        
        stats_text = f"""
📊 **Bot Statistics**

👥 **Users:**
• Total Users: {total_users}
• Premium Users: {premium_users}
• Admin Users: {admin_users}
• Banned Users: {banned_users}

📥 **Downloads:**
• Total Downloads: {total_downloads}
• Successful: {successful_downloads}
• Failed: {failed_downloads}
• Success Rate: {(successful_downloads/total_downloads*100):.1f}% if total_downloads > 0 else 0%

📅 **Today:**
• Downloads: {today_downloads}
• Active Users: {today_users}
"""
        
        await update.message.reply_text(stats_text, parse_mode=ParseMode.MARKDOWN)
        
    finally:
        db.close()

async def user_info_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Get user information - Usage: /userinfo <user_id>"""
    user_id = str(update.effective_user.id)
    
    if not await is_admin(user_id):
        await update.message.reply_text("❌ Access denied. Admin privileges required.")
        return
    
    if not context.args:
        await update.message.reply_text("Usage: /userinfo <user_id>\nExample: /userinfo 123456789")
        return
    
    target_user_id = context.args[0]
    
    db = get_db()
    try:
        target_user = db.query(User).filter(User.user_id == target_user_id).first()
        if not target_user:
            await update.message.reply_text(f"❌ User {target_user_id} not found.")
            return
        
        # Get user's download count
        download_count = db.query(Download).filter(Download.user_id == target_user_id).count()
        
        status = "🔴 Banned" if target_user.is_banned else "🟢 Active"
        user_type_emoji = {"normal": "👤", "premium": "💎", "admin": "⭐"}
        
        info_text = f"""
👤 **User Information**

**Basic Info:**
• User ID: `{target_user.user_id}`
• Username: @{target_user.username or 'N/A'}
• Name: {target_user.first_name or ''} {target_user.last_name or ''}
• Status: {status}

**Account:**
• Type: {user_type_emoji.get(target_user.user_type, '👤')} {target_user.user_type.title()}
• Joined: {target_user.joined_at.strftime('%Y-%m-%d %H:%M')}
• Last Active: {target_user.last_active.strftime('%Y-%m-%d %H:%M')}

**Usage:**
• Total Downloads: {download_count}
• Daily Downloads: {target_user.daily_downloads}
• Last Download: {target_user.last_download_time.strftime('%Y-%m-%d %H:%M') if target_user.last_download_time else 'Never'}

**Premium Info:**
• Premium Until: {target_user.premium_until.strftime('%Y-%m-%d %H:%M') if target_user.premium_until else 'N/A'}
• Added by Admin: {target_user.added_by_admin or 'N/A'}
"""
        
        await update.message.reply_text(info_text, parse_mode=ParseMode.MARKDOWN)
        
    finally:
        db.close()

async def my_status_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show current user's status and limits"""
    user_id = str(update.effective_user.id)
    username = update.effective_user.username
    first_name = update.effective_user.first_name
    last_name = update.effective_user.last_name
    
    # Ensure user exists
    user = await ensure_user_exists(user_id, username, first_name, last_name)
    
    db = get_db()
    try:
        user = db.query(User).filter(User.user_id == str(user_id)).first()
        download_count = db.query(Download).filter(Download.user_id == str(user_id)).count()
        
        user_type_emoji = {"normal": "👤", "premium": "💎", "admin": "⭐"}
        status = "🔴 Banned" if user.is_banned else "🟢 Active"
        
        # Calculate remaining downloads for normal users
        remaining = ""
        if user.user_type == 'normal' and not user.is_banned:
            remaining = f"• Remaining Today: {max(0, 10 - user.daily_downloads)}/10"
        
        status_text = f"""
📱 **Your Account Status**

**Account Type:** {user_type_emoji.get(user.user_type, '👤')} {user.user_type.title()}
**Status:** {status}
**Total Downloads:** {download_count}

**Daily Limits:**
{remaining}
{'• Downloads: Unlimited (Premium)' if user.is_premium() else ''}
{'• Downloads: Unlimited (Admin)' if user.is_admin() else ''}

**Premium Info:**
{'• Expires: ' + user.premium_until.strftime('%Y-%m-%d %H:%M') if user.premium_until else '• Not Premium'}

**Rate Limits:**
{'• No cooldown (Premium/Admin)' if user.is_premium() or user.is_admin() else '• 3 minutes between downloads after first'}
"""
        
        await update.message.reply_text(status_text, parse_mode=ParseMode.MARKDOWN)
        
    finally:
        db.close()

async def handle_admin_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle admin panel button callbacks"""
    query = update.callback_query
    await query.answer()
    
    user_id = str(query.from_user.id)
    
    if not await is_admin(user_id):
        try:
            await query.edit_message_text("❌ Access denied. Admin privileges required.")
        except Exception:
            await query.message.reply_text("❌ Access denied. Admin privileges required.")
        return
    
    data = query.data
    
    try:
        if data == "admin_stats":
            await show_admin_stats(query, context)
        elif data == "admin_users":
            await show_user_management(query, context)
        elif data == "admin_premium":
            await show_premium_management(query, context)
        elif data == "admin_settings":
            await show_admin_settings(query, context)
        elif data == "admin_logs":
            await show_admin_logs(query, context)
        elif data == "admin_back":
            await show_admin_panel_callback(query, context)
    except Exception as e:
        logger.error(f"Admin callback error: {e}")
        try:
            await query.message.reply_text("❌ Admin panel error occurred. Please try again.")
        except:
            pass

async def show_admin_stats(query, context):
    """Show bot statistics in callback"""
    db = get_db()
    try:
        # Get user statistics
        total_users = db.query(User).count()
        premium_users = db.query(User).filter(User.user_type == 'premium').count()
        admin_users = db.query(User).filter(User.user_type == 'admin').count()
        banned_users = db.query(User).filter(User.is_banned == True).count()
        
        # Get download statistics
        total_downloads = db.query(Download).count()
        successful_downloads = db.query(Download).filter(Download.status == 'success').count()
        failed_downloads = db.query(Download).filter(Download.status == 'failed').count()
        
        # Today's statistics
        today = datetime.utcnow().date()
        today_downloads = db.query(Download).filter(func.date(Download.created_at) == today).count()
        today_users = db.query(User).filter(func.date(User.last_active) == today).count()
        
        success_rate = (successful_downloads/total_downloads*100) if total_downloads > 0 else 0
        
        stats_text = f"""
📊 **Bot Statistics**

👥 **Users:**
• Total Users: {total_users}
• Premium Users: {premium_users}
• Admin Users: {admin_users}
• Banned Users: {banned_users}

📥 **Downloads:**
• Total Downloads: {total_downloads}
• Successful: {successful_downloads}
• Failed: {failed_downloads}
• Success Rate: {success_rate:.1f}%

📅 **Today:**
• Downloads: {today_downloads}
• Active Users: {today_users}

Use /stats command for detailed statistics.
"""
        
        keyboard = [[InlineKeyboardButton("🔙 Back to Admin Panel", callback_data="admin_back")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(stats_text, reply_markup=reply_markup, parse_mode=ParseMode.MARKDOWN)
        
    finally:
        db.close()

async def show_user_management(query, context):
    """Show user management options"""
    db = get_db()
    try:
        # Get user statistics
        total_users = db.query(User).count()
        admin_users = db.query(User).filter(User.user_type == 'admin').count()
        banned_users = db.query(User).filter(User.is_banned == True).count()
        
        text = f"""
👥 **User Management**

**Current Users:** {total_users} total
**Admins:** {admin_users} | **Banned:** {banned_users}

**Available Commands:**
• `/addadmin <user_id>` - Grant admin privileges
• `/ban <user_id>` - Ban a user
• `/unban <user_id>` - Unban a user
• `/userinfo <user_id>` - Get user details

**Example:** `/addadmin 123456789`
"""
        
        keyboard = [[InlineKeyboardButton("🔙 Back to Admin Panel", callback_data="admin_back")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(text, reply_markup=reply_markup, parse_mode=ParseMode.MARKDOWN)
        
    except Exception as e:
        # Fallback without database stats
        text = """
👥 **User Management**

**Available Commands:**
• `/addadmin <user_id>` - Grant admin privileges
• `/ban <user_id>` - Ban a user
• `/unban <user_id>` - Unban a user
• `/userinfo <user_id>` - Get user details

**Example:** `/addadmin 123456789`
"""
        
        keyboard = [[InlineKeyboardButton("🔙 Back to Admin Panel", callback_data="admin_back")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(text, reply_markup=reply_markup, parse_mode=ParseMode.MARKDOWN)
    finally:
        db.close()

async def show_premium_management(query, context):
    """Show premium management options"""
    db = get_db()
    try:
        # Get premium user count
        premium_count = db.query(User).filter(User.user_type == 'premium').count()
        active_premium = db.query(User).filter(
            User.premium_until > datetime.utcnow()
        ).count()
        
        text = f"""
💎 **Premium Management**

**Current Premium Users:** {premium_count}
**Active Premium Subscriptions:** {active_premium}

**Available Commands:**
• `/premium <user_id> <days>` - Grant premium access
• `/userinfo <user_id>` - Check user premium status

**Example:** `/premium 123456789 30`

This grants 30 days of premium access to the user.
Premium users get unlimited downloads with no cooldown.
"""
        
        keyboard = [[InlineKeyboardButton("🔙 Back to Admin Panel", callback_data="admin_back")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(text, reply_markup=reply_markup, parse_mode=ParseMode.MARKDOWN)
        
    except Exception as e:
        # Fallback without database stats
        text = """
💎 **Premium Management**

**Available Commands:**
• `/premium <user_id> <days>` - Grant premium access
• `/userinfo <user_id>` - Check user premium status

**Example:** `/premium 123456789 30`

This grants 30 days of premium access to the user.
Premium users get unlimited downloads with no cooldown.
"""
        
        keyboard = [[InlineKeyboardButton("🔙 Back to Admin Panel", callback_data="admin_back")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(text, reply_markup=reply_markup, parse_mode=ParseMode.MARKDOWN)
    finally:
        db.close()

async def show_admin_settings(query, context):
    """Show admin settings"""
    text = """
⚙️ **Admin Settings**

Current Configuration:
• Max File Size: 200MB
• Daily Limit (Normal): 10 downloads
• Cooldown (Normal): 3 minutes
• Max Duration: 30 minutes

Settings are configured in the code.
Contact the developer to modify these limits.
"""
    
    keyboard = [[InlineKeyboardButton("🔙 Back to Admin Panel", callback_data="admin_back")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(text, reply_markup=reply_markup, parse_mode=ParseMode.MARKDOWN)

async def show_admin_logs(query, context):
    """Show recent admin logs"""
    db = get_db()
    try:
        recent_logs = db.query(AdminLog).order_by(AdminLog.created_at.desc()).limit(10).all()
        
        if not recent_logs:
            logs_text = "📝 **Admin Logs**\n\nNo admin actions recorded yet."
        else:
            logs_text = "📝 **Admin Logs (Recent 10)**\n\n"
            for log in recent_logs:
                timestamp = log.created_at.strftime('%m-%d %H:%M')
                logs_text += f"• {timestamp}: {log.action}\n"
                if log.target_user_id:
                    logs_text += f"  Target: {log.target_user_id}\n"
                if log.details:
                    logs_text += f"  Details: {log.details}\n"
                logs_text += "\n"
        
        keyboard = [[InlineKeyboardButton("🔙 Back to Admin Panel", callback_data="admin_back")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(logs_text, reply_markup=reply_markup, parse_mode=ParseMode.MARKDOWN)
        
    finally:
        db.close()

async def show_admin_panel_callback(query, context):
    """Show admin panel from callback"""
    text = """
🔧 **Admin Control Panel**

Welcome to the admin dashboard. Choose an option below:

👥 **User Management** - Add/remove admins, ban users
💎 **Premium Management** - Grant/revoke premium access
📊 **Statistics** - View bot usage statistics
⚙️ **Settings** - Configure bot settings
📝 **Admin Logs** - View admin action history
"""
    
    keyboard = [
        [InlineKeyboardButton("👥 User Management", callback_data="admin_users")],
        [InlineKeyboardButton("💎 Premium Management", callback_data="admin_premium")],
        [InlineKeyboardButton("📊 Statistics", callback_data="admin_stats")],
        [InlineKeyboardButton("⚙️ Settings", callback_data="admin_settings")],
        [InlineKeyboardButton("📝 Admin Logs", callback_data="admin_logs")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(text, reply_markup=reply_markup, parse_mode=ParseMode.MARKDOWN)