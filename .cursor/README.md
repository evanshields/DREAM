# Cursor Agent Configuration

This directory contains agent configurations and prompts for specialized workflows in Cursor.

## Available Agents

### UX Engineer Agent
**Purpose**: Analyze PRDs and create semantic HTML prototypes for mobile applications

**Activation**: 
- Say "Activate UX Engineer agent" or reference `ux-engineer-prompt.md`
- Or simply request "Create UX prototype for [PRD]"

**Output**: Generates `ux-prototype.html` with all screens, navigation, and states

**Location**: `.cursor/ux-engineer-prompt.md`

**ShadCN Integration**: 
- Considers ShadCN components when designing structure
- Documents ShadCN component mappings in HTML comments for UI Engineer reference

### UI Engineer Agent (Minimal Pro & Analytical Pro)
**Purpose**: Apply beautiful, brand-forward styling to UX prototypes using ShadCN components

**Activation**: 
- Say "Activate UI Engineer agent" or "UI Implementer"
- Request styling for UX prototypes

**Output**: Generates `dream-ui-minimal.html` or `dream-ui-analytical.html` with ShadCN components

**ShadCN Integration**: 
- **PRIORITY**: Always uses ShadCN MCP server to get component code before implementation
- Replaces semantic HTML with ShadCN component structures (Button, Card, Table, Badge, etc.)
- Styles ShadCN components with Dream design tokens
- Creates brand-forward, beautiful UIs using ShadCN's polished component library

### Framework Converter Agent
**Purpose**: Convert styled HTML prototypes to production-ready Next.js applications

**Activation**: 
- Say "Convert to Next.js" or "Framework Converter"

**Output**: Complete Next.js app structure with ShadCN components

**ShadCN Integration**: 
- Uses ShadCN MCP server to get component code for all UI elements
- Installs ShadCN components to `components/ui/` directory
- Uses ShadCN as foundation for all components (Button, Card, Table, Badge, Input, Select, Dialog, etc.)

## ShadCN MCP Server

**Status**: ✅ Configured and Running

The ShadCN MCP server is configured in `c:\Users\evana\.cursor\mcp.json` and provides:
- Access to all 55+ ShadCN UI v4 components
- Component source code via `mcp_shadcn-ui_get_component`
- Component demos via `mcp_shadcn-ui_get_component_demo`
- Component metadata via `mcp_shadcn-ui_get_component_metadata`
- Available blocks via `mcp_shadcn-ui_list_blocks`

**All agents are now incentivized to:**
1. **Always check ShadCN MCP server** before creating custom components
2. **Use ShadCN components** as the foundation for all UI elements
3. **Style ShadCN components** with Dream design tokens for brand-forward UIs
4. **Prioritize beautiful, accessible UIs** using ShadCN's polished component library

## How Cursor Agents Work

Cursor uses `.cursorrules` files and custom instructions to define agent behavior. All agents are configured to:

1. **Auto-activate** when you mention their specific work type
2. **Use ShadCN MCP server** to get component code and patterns
3. **Apply Dream design tokens** to ShadCN components for brand consistency
4. **Create beautiful, brand-forward UIs** using ShadCN's accessible component library

## Adding New Agents

To add a new agent:
1. Add rules to `.cursorrules`
2. Include ShadCN MCP server integration in agent rules
3. Create a prompt file in `.cursor/` directory
4. Document usage in this README

