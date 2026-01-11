# UI Engineer Agent - Recommendations & Setup

## File Naming Recommendations

### Standardized Naming Convention

**Recommendation: Use consistent, descriptive names**

1. **UX Prototype Input**: `dream-ux.html`
   - **Rationale**: More specific than `ux-prototype.html`, clearly indicates it's for Dream app
   - **Alternative**: Accept `ux-prototype.html` for flexibility
   - **Location**: Project root or `prototypes/` directory

2. **UI Output**: `dream-ui-minimal.html`
   - **Rationale**: Clear naming convention that indicates:
     - App: `dream`
     - Type: `ui` (styled version)
     - Theme: `minimal` (Minimal Pro)
   - **Always use this exact name** for consistency

3. **Design Language**: `design-language-dream.md`
   - **Location**: Project root (for easy reference)
   - **Status**: ✅ Created

### Workflow

```
PRD → UX Engineer → dream-ux.html → UI Engineer → dream-ui-minimal.html
```

---

## Tailwind CSS Setup Recommendations

### Option 1: CDN (Recommended for Prototypes)

**Best for**: Quick prototypes, standalone HTML files, rapid iteration

**Implementation**:
```html
<script src="https://cdn.tailwindcss.com"></script>
```

**Pros**:
- ✅ Zero configuration needed
- ✅ Works immediately in standalone HTML files
- ✅ Perfect for UX → UI prototype workflow
- ✅ No build step required

**Cons**:
- ❌ Larger file size (~3MB)
- ❌ No custom configuration (uses defaults)
- ❌ Not ideal for production

**Recommendation**: Use CDN for `dream-ui-minimal.html` prototypes. This allows the UI Engineer to create standalone, viewable HTML files without any build setup.

### Option 2: Tailwind CLI (For Production)

**Best for**: Production builds, custom configuration, optimized output

**Setup**:
```bash
npm install -D tailwindcss
npx tailwindcss init
```

**Configuration**: Use `tailwind.config.js` with design language tokens (already exists in your project)

**Pros**:
- ✅ Smaller file size (only used classes)
- ✅ Custom configuration support
- ✅ Production-ready
- ✅ Can use design language tokens

**Cons**:
- ❌ Requires build step
- ❌ More setup complexity
- ❌ Not suitable for standalone HTML prototypes

**Recommendation**: Use CLI/build setup for production React app. Keep CDN for prototype HTML files.

### Option 3: Hybrid Approach (Recommended)

**For Prototypes** (UI Engineer output):
- Use Tailwind CDN in `dream-ui-minimal.html`
- Allows immediate viewing and sharing
- No build step needed

**For Production** (React app):
- Use Tailwind CLI with existing `tailwind.config.js`
- Leverage design language tokens
- Optimized builds

**Implementation Strategy**:
1. UI Engineer creates `dream-ui-minimal.html` with CDN
2. Design tokens from `design-language-dream.md` are applied as Tailwind classes
3. Production React app uses same classes but via CLI build
4. Both outputs look identical

---

## Design Language Integration

### How UI Engineer Uses Design Language

1. **Reads** `design-language-dream.md` for:
   - Color tokens (converts to Tailwind classes)
   - Typography scale (applies font classes)
   - Spacing scale (uses Tailwind spacing utilities)
   - Component patterns (applies consistent styling)

2. **Applies Tokens**:
   - Colors: `bg-[#005253]`, `text-primary`, `border-border`
   - Typography: `font-heading`, `text-3xl`, `tabular-nums`
   - Spacing: `p-4`, `gap-6`, `mb-8`
   - Components: Follows card, button, input patterns

3. **Fallback**: If design language file missing, uses sensible Minimal Pro defaults

---

## Recommendations Summary

### ✅ File Naming
- **Standardize on**: `dream-ux.html` → `dream-ui-minimal.html`
- **Keep flexible**: Accept `ux-prototype.html` as alternative input
- **Always output**: `dream-ui-minimal.html` (exact name)

### ✅ Tailwind Setup
- **For Prototypes**: Use Tailwind CDN (`https://cdn.tailwindcss.com`)
- **For Production**: Use existing Tailwind CLI setup with `tailwind.config.js`
- **Rationale**: Prototypes need to be standalone and viewable immediately

### ✅ Design Language
- **Location**: `design-language-dream.md` in project root
- **Status**: ✅ Created with full token system
- **Usage**: UI Engineer references this file for all styling decisions

---

## Example Workflow

1. **User**: "Create UX prototype for deal analysis screen"
2. **UX Engineer**: Creates `dream-ux.html` with semantic HTML
3. **User**: "Apply Minimal Pro styling"
4. **UI Engineer**: 
   - Reads `dream-ux.html`
   - References `design-language-dream.md`
   - Applies Tailwind classes via CDN
   - Outputs `dream-ui-minimal.html`
5. **Result**: Fully styled, standalone HTML file ready for review

---

## Next Steps

1. ✅ Design language file created
2. ✅ `.cursorrules` updated with file naming
3. ✅ Tailwind CDN specified for prototypes
4. ⏭️ Test workflow: Create sample UX prototype → Apply styling
5. ⏭️ Validate design tokens work correctly with Tailwind CDN

---

**Last Updated**: December 2025

