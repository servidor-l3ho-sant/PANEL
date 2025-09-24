# APK Editor Pro

## Overview

APK Editor Pro is a comprehensive Python-based tool for editing decompiled Android applications with AI assistance. The application supports both terminal and web interfaces, making it compatible with Termux and desktop environments. It integrates with Google's Gemini AI API to provide intelligent suggestions for Android resource modifications, layout improvements, and error corrections. The tool manages APK file structures, validates XML resources, generates templates, and provides backup/restore functionality for safe editing workflows.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Application Structure
- **Dual Interface Design**: The application runs in three modes - terminal-only, web-only, or hybrid mode where both interfaces run simultaneously
- **Component-Based Architecture**: Modular design with separate classes for file management, validation, AI integration, and template generation
- **Rich Terminal Interface**: Uses the Rich library for enhanced terminal output with colors, tables, panels, and progress indicators

### Core Components

#### File Management (`file_manager.py`)
- **APKFileManager Class**: Handles APK project structure detection and file operations
- **Backup System**: Automatic backup creation before modifications with versioned restore capability
- **Project Structure Validation**: Verifies APK decompiled structure (res/ directories) before operations
- **File History Tracking**: JSON-based logging of all file operations with timestamps

#### AI Integration (`api_gemini.py`)
- **GeminiAndroidAssistant Class**: Wrapper for Google Gemini API interactions
- **Android-Specific Prompts**: Specialized prompts for analyzing Android layouts, resources, and suggesting improvements
- **Error Handling**: Graceful degradation when API is unavailable
- **Response Processing**: Structured handling of AI suggestions with actionable recommendations

#### Validation System (`validator.py`)
- **AndroidResourceValidator Class**: Multi-layer validation for Android XML resources
- **XML Syntax Validation**: Basic XML well-formedness checking
- **Android-Specific Rules**: Validates layout constraints, resource references, and manifest structure
- **Error Classification**: Separates critical errors from warnings with detailed reporting

#### Template Generation (`templates.py`)
- **AndroidTemplateGenerator Class**: Creates boilerplate Android layouts and resources
- **AI-Enhanced Templates**: Uses Gemini API to generate context-aware templates
- **Multiple Layout Types**: Supports LinearLayout, ConstraintLayout, and custom structures

#### Web Interface (`web_server.py`)
- **Flask-Based Server**: RESTful API endpoints for web client interactions
- **Real-Time Communication**: AJAX-based interface updates without page refreshes
- **Responsive Design**: Mobile-friendly interface compatible with Termux browsers

### Data Flow Architecture
- **Request Processing**: User actions flow through main.py → component classes → utils for logging
- **State Management**: Current project state maintained in APKEditor class with persistent storage
- **Error Propagation**: Structured error handling with user-friendly messages and technical logging

### Integration Patterns
- **GitHub Integration**: Planned integration using Replit's connection system for version control
- **APK Tools Integration**: Command-line interface to apktool for building/rebuilding APKs
- **External Service Abstraction**: API clients designed with fallback mechanisms for offline operation

## External Dependencies

### AI Services
- **Google Gemini API**: Primary AI service for code analysis and suggestions
- **Authentication**: Requires GEMINI_API_KEY environment variable
- **Usage**: Layout analysis, error correction suggestions, template generation

### Development Tools
- **APKTool**: External command-line tool for APK decompilation/recompilation
- **Android SDK Tools**: For APK signing and validation (optional)

### Python Libraries
- **Rich**: Terminal interface enhancement (tables, panels, progress bars, colors)
- **Flask**: Web server framework for browser interface
- **Requests**: HTTP client for API interactions
- **Pathlib**: Modern file system operations
- **XML Parser**: Built-in ElementTree for XML validation

### Platform Integration
- **Replit Connections**: GitHub integration through Replit's OAuth system
- **Termux Compatibility**: Designed to run in Android's Termux environment
- **Environment Variables**: Uses Replit's secret management for API keys

### File System Requirements
- **Backup Directory**: Creates and manages local backup storage
- **Log Directory**: Structured logging to files and console
- **Project Structure**: Expects standard APK decompiled directory structure

### Optional Services
- **GitHub API**: For repository synchronization (requires Replit connection)
- **Web Browser**: For accessing web interface (any modern browser)
- **Android Keystore**: For APK signing (user-provided)