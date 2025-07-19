# Telegram Video Downloader Bot - Professional Edition

## Overview

This is a complete, professional-grade Telegram bot with advanced user management, admin controls, and premium features. The bot downloads videos from various platforms using yt-dlp and sends them directly to users with sophisticated rate limiting and user tier management.

## Current Status: ✅ PROFESSIONAL VERSION DEPLOYED

The bot has been upgraded to a professional system with comprehensive features:
- ✅ Advanced admin management system
- ✅ User tiers: Normal, Premium, Admin
- ✅ Rate limiting: 10 downloads/day for normal users, 3-minute cooldown
- ✅ Premium users: Unlimited downloads, no cooldown
- ✅ Admin controls: Add admins, grant premium, ban users, view statistics
- ✅ Database integration: PostgreSQL with user tracking and download history
- ✅ Video downloading from supported platforms (YouTube, TikTok, Twitter, etc.)
- ✅ Direct video file download support with SSL certificate handling
- ✅ 200MB file size limit with professional error handling
- ✅ Professional logging and monitoring
- ✅ Ready for commercial deployment

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

The application follows a modular architecture pattern with clear separation of concerns:

- **Bot Interface Layer**: Handles Telegram bot interactions and user commands
- **Download Engine**: Manages video downloading using yt-dlp library
- **Utility Layer**: Provides common functions for file management and validation
- **Configuration Layer**: Centralizes all configuration settings

The bot operates asynchronously using Python's asyncio to handle multiple download requests concurrently without blocking.

## Professional Features

### User Management System
- **Three User Tiers**: Normal, Premium, Admin
- **Rate Limiting**: Normal users limited to 10 downloads/day with 3-minute cooldown between downloads
- **Premium Benefits**: Unlimited downloads, no cooldown, priority support
- **Admin Powers**: Full system control, user management, statistics access

### Admin Commands
- `/admin` - Access admin control panel
- `/addadmin <user_id>` - Grant admin privileges to users
- `/premium <user_id> <days>` - Grant premium access for specified days
- `/ban <user_id>` - Ban users from the bot
- `/unban <user_id>` - Remove user bans
- `/stats` - View comprehensive bot statistics
- `/userinfo <user_id>` - Get detailed user information
- `/status` - Check your account status and limits

### Database Integration
- **PostgreSQL Database**: Stores user information, download history, admin logs
- **User Tracking**: Complete user activity monitoring and analytics
- **Download Records**: Detailed logging of all download attempts and results
- **Admin Audit Trail**: Full logging of all administrative actions

## Key Components

### 1. Professional Bot Core (`bot.py`)
- **Purpose**: Main bot application with advanced user management
- **Key Functions**:
  - User authentication and rate limiting
  - Professional download handling with database integration
  - Admin command processing
  - Comprehensive error handling and logging

### 2. Admin Management (`admin_handlers.py`)
- **Purpose**: Complete admin control system
- **Key Functions**:
  - User tier management (Normal/Premium/Admin)
  - Premium subscription management
  - User banning and moderation tools
  - Statistics and analytics dashboard

### 3. Database Models (`models.py`)
- **Purpose**: PostgreSQL database schema and user management
- **Key Functions**:
  - User profile and tier management
  - Download history and rate limiting
  - Admin action logging
  - Premium subscription tracking

### 2. Video Downloader (`video_downloader.py`)
- **Purpose**: Core video downloading functionality using yt-dlp
- **Architecture**: Uses ThreadPoolExecutor to run synchronous yt-dlp operations in separate threads
- **Features**:
  - Video quality optimization (prefers 720p to reduce file size)
  - Duration limits (30 minutes maximum)
  - File size validation before sending
  - Metadata extraction for video information

### 3. Main Application (`main.py`)
- **Purpose**: Bot initialization and lifecycle management
- **Features**:
  - Supports both polling and webhook modes for deployment flexibility
  - Handles application setup and teardown
  - Manages handler registration

### 4. Utilities (`utils.py`)
- **Purpose**: Common utility functions
- **Functions**:
  - URL validation and platform detection
  - File management (creation, cleanup)
  - Temporary directory management

### 5. Configuration (`config.py`)
- **Purpose**: Centralized configuration management
- **Settings**:
  - Bot token management
  - File size limits (50MB - Telegram's bot limit)
  - Download timeouts (5 minutes)
  - Supported platforms list
  - Logging configuration

## Data Flow

1. **User Input**: User sends video URL to bot
2. **Validation**: Bot validates URL format and checks if platform is supported
3. **Download Request**: Bot queues download using ThreadPoolExecutor
4. **Video Processing**: yt-dlp downloads video with specified quality settings
5. **File Validation**: Bot checks file size against Telegram limits
6. **Response**: Bot sends video file back to user or error message if failed
7. **Cleanup**: Temporary files are automatically cleaned up

## External Dependencies

### Core Libraries
- **python-telegram-bot**: Telegram Bot API wrapper for Python
- **yt-dlp**: Video downloading library (fork of youtube-dl with active maintenance)
- **asyncio**: Built-in Python library for asynchronous programming

### Platform Support
The bot leverages yt-dlp's extensive platform support, including:
- YouTube, Twitter/X, Instagram, TikTok
- Vimeo, Facebook, Reddit, Twitch
- Many other platforms supported by yt-dlp

## Deployment Strategy

### Local Development
- Uses polling mode for simple local testing
- Temporary files stored in local `temp_downloads` directory
- Environment variable configuration for bot token

### Production Deployment
- Webhook mode support for efficient server deployment
- Configurable port and webhook URL
- Environment-based configuration
- Built-in error handling and logging

### Key Deployment Considerations
- **File Storage**: Uses temporary local storage with automatic cleanup
- **Concurrency**: ThreadPoolExecutor with limited workers (2) to prevent resource exhaustion
- **Resource Limits**: 
  - 50MB file size limit (Telegram constraint)
  - 30-minute video duration limit
  - 5-minute download timeout
- **Error Recovery**: Comprehensive error handling with user-friendly messages

### Security Features
- URL validation to prevent malicious inputs
- Platform whitelist for supported services
- File size validation before processing
- Automatic cleanup of temporary files