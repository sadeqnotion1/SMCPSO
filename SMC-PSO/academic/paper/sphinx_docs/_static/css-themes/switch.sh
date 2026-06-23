#!/bin/bash
#======================================================================================\\\
#========================= docs/_static/css-themes/switch.sh ==========================\\\
#======================================================================================\\\

# CSS Theme Switcher for DIP-SMC-PSO Documentation
# Usage: ./switch.sh <theme-name>
# Example: ./switch.sh minimal-professional

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Get theme name from argument
THEME=$1

# Directory paths
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
THEMES_DIR="$SCRIPT_DIR"
STATIC_DIR="$(dirname "$SCRIPT_DIR")"
CUSTOM_CSS="$STATIC_DIR/custom.css"

# Function to print colored output
print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

# Function to list available themes
list_themes() {
    print_info "Available themes:"
    echo ""
    for css_file in "$THEMES_DIR"/*.css; do
        if [ -f "$css_file" ]; then
            theme_name=$(basename "$css_file" .css)
            echo "  - $theme_name"
        fi
    done
    echo ""
}

# Main logic
if [ -z "$THEME" ]; then
    print_error "No theme specified!"
    echo ""
    echo "Usage: ./switch.sh <theme-name>"
    echo "Example: ./switch.sh minimal-professional"
    echo ""
    list_themes
    exit 1
fi

# Check if theme file exists
THEME_FILE="$THEMES_DIR/${THEME}.css"

if [ ! -f "$THEME_FILE" ]; then
    print_error "Theme '${THEME}' not found!"
    echo ""
    list_themes
    exit 1
fi

# Backup current custom.css
BACKUP_FILE="$STATIC_DIR/custom.css.backup"
if [ -f "$CUSTOM_CSS" ]; then
    print_info "Backing up current custom.css..."
    cp "$CUSTOM_CSS" "$BACKUP_FILE"
    print_success "Backup created: custom.css.backup"
fi

# Copy theme to custom.css
print_info "Switching to theme: $THEME"
cp "$THEME_FILE" "$CUSTOM_CSS"

# Verify copy
if [ $? -eq 0 ]; then
    print_success "Theme switched successfully!"
    echo ""
    print_info "Next steps:"
    echo "  1. Rebuild documentation: cd docs && make html"
    echo "  2. View changes: Open docs/_build/html/index.html"
    echo ""
    print_warning "Remember to commit changes if you want to keep this theme!"
else
    print_error "Failed to copy theme file!"

    # Restore backup if copy failed
    if [ -f "$BACKUP_FILE" ]; then
        print_info "Restoring backup..."
        cp "$BACKUP_FILE" "$CUSTOM_CSS"
        print_success "Backup restored"
    fi
    exit 1
fi
