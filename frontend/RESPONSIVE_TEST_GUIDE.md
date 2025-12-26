# Responsive Layout Testing Guide

This guide provides instructions for manually testing the responsive design implementation across different device sizes.

## Testing Requirements

Test the application on the following viewport sizes:
- **Desktop**: ≥1024px (e.g., 1920x1080, 1440x900)
- **Tablet**: 768px - 1023px (e.g., 768x1024, 834x1194)
- **Mobile**: <768px (e.g., 375x667, 414x896)

## Test Scenarios

### 1. Desktop Layout (≥1024px)

#### Navigation
- [ ] Top navigation bar displays with all menu items visible horizontally
- [ ] Logo and app name "UHotRank" are both visible
- [ ] Theme toggle button is visible in the top right
- [ ] No hamburger menu button is visible
- [ ] Navigation items highlight correctly when active

#### Layout
- [ ] Main content area has appropriate padding and max-width
- [ ] Article cards display in a 3-column grid (in grid view mode)
- [ ] Statistics charts display side-by-side in 2-column layout
- [ ] All text is readable and properly sized
- [ ] Buttons and interactive elements have appropriate spacing

#### Pages
- [ ] Article List: 3-column grid layout
- [ ] Article Detail: Content is centered with good readability
- [ ] Statistics: Charts display in 2-column grid
- [ ] Crawler Management: 2-column layout for controls and history
- [ ] Settings: Form fields are properly aligned

### 2. Tablet Layout (768px - 1023px)

#### Navigation
- [ ] Top navigation bar displays correctly
- [ ] Logo is visible, app name may be hidden on smaller tablets
- [ ] Theme toggle button is visible
- [ ] Hamburger menu button appears on smaller tablets (<1024px)
- [ ] Mobile sidebar slides in from left when hamburger is clicked

#### Layout
- [ ] Main content area adjusts padding appropriately
- [ ] Article cards display in a 2-column grid (in grid view mode)
- [ ] Statistics charts may stack or display in 2-column layout
- [ ] Touch targets are at least 44x44px for easy tapping
- [ ] Spacing is optimized for tablet viewing

#### Pages
- [ ] Article List: 2-column grid layout
- [ ] Article Detail: Content width is optimized for reading
- [ ] Statistics: Charts adapt to available space
- [ ] Crawler Management: May switch to single column on smaller tablets
- [ ] Settings: Form layout adapts to available width

### 3. Mobile Layout (<768px)

#### Navigation
- [ ] Top navigation bar displays with hamburger menu button
- [ ] Logo is visible, app name may be hidden
- [ ] Theme toggle button is visible
- [ ] Hamburger menu button is visible and functional
- [ ] Mobile sidebar slides in from left when hamburger is clicked
- [ ] Sidebar overlay darkens the background
- [ ] Clicking overlay closes the sidebar
- [ ] Sidebar closes when navigating to a new page
- [ ] Navigation items in sidebar have larger touch targets (min 48px height)

#### Layout
- [ ] Main content area uses full width with minimal padding
- [ ] Article cards display in a single column
- [ ] All interactive elements have touch-friendly sizes (≥44x44px)
- [ ] Text sizes are readable on small screens
- [ ] Buttons stack vertically when needed

#### Pages
- [ ] Article List: Single column layout
- [ ] Article Detail: Content is readable with appropriate line length
- [ ] Statistics: All charts stack vertically
- [ ] Crawler Management: Single column layout
- [ ] Settings: Form fields stack vertically

#### Touch Interactions
- [ ] All buttons have `touch-manipulation` class for better touch response
- [ ] Buttons provide visual feedback on tap (active:scale-95)
- [ ] No hover-only interactions (all features accessible via touch)
- [ ] Scrolling is smooth and responsive
- [ ] No horizontal scrolling occurs

### 4. Responsive Breakpoint Transitions

#### Viewport Resizing
- [ ] Layout smoothly transitions when resizing from desktop to tablet
- [ ] Layout smoothly transitions when resizing from tablet to mobile
- [ ] No layout breaks or overlapping elements during transitions
- [ ] Navigation adapts correctly at breakpoints
- [ ] Grid layouts adjust column counts appropriately

#### Orientation Changes (Mobile/Tablet)
- [ ] Layout adapts correctly when rotating device
- [ ] Content remains accessible in both portrait and landscape
- [ ] No content is cut off or hidden after rotation

### 5. Component-Specific Tests

#### Article Cards
- [ ] Cards are touch-friendly with appropriate padding
- [ ] Text truncation works correctly on all screen sizes
- [ ] Tech badges and tags wrap properly
- [ ] Card hover/active states work on touch devices

#### Charts (Statistics Page)
- [ ] Charts resize appropriately for viewport
- [ ] Chart legends hide on mobile when needed
- [ ] Touch interactions work for chart tooltips
- [ ] All chart text remains readable

#### Forms (Settings Page)
- [ ] Form fields are full-width on mobile
- [ ] Labels and inputs stack vertically on mobile
- [ ] Buttons are full-width or appropriately sized on mobile
- [ ] Form validation messages display correctly

#### Dialogs/Modals
- [ ] Dialogs are properly sized for viewport
- [ ] Dialog content is scrollable if needed
- [ ] Close buttons are easily accessible
- [ ] Dialogs don't overflow viewport

## Testing Tools

### Browser DevTools
1. Open Chrome/Firefox DevTools (F12)
2. Click the device toolbar icon (Ctrl+Shift+M)
3. Select different device presets or enter custom dimensions
4. Test both portrait and landscape orientations

### Recommended Test Devices/Sizes
- **Mobile**: iPhone SE (375x667), iPhone 12 Pro (390x844), Pixel 5 (393x851)
- **Tablet**: iPad (768x1024), iPad Pro (834x1194)
- **Desktop**: 1366x768, 1920x1080, 2560x1440

## Common Issues to Check

- [ ] No horizontal scrolling on any viewport size
- [ ] All text is readable (minimum 14px on mobile)
- [ ] Touch targets are at least 44x44px
- [ ] No overlapping elements
- [ ] Images and charts don't overflow containers
- [ ] Navigation is always accessible
- [ ] Content doesn't get cut off
- [ ] Proper spacing between elements
- [ ] Consistent padding and margins

## Accessibility Checks

- [ ] Keyboard navigation works on all screen sizes
- [ ] Focus indicators are visible
- [ ] Screen reader navigation is logical
- [ ] Color contrast meets WCAG standards
- [ ] Touch targets meet accessibility guidelines (48x48px recommended)

## Performance Checks

- [ ] Page loads quickly on mobile networks
- [ ] Smooth scrolling on all devices
- [ ] No layout shifts during page load
- [ ] Images load appropriately for viewport size
- [ ] Animations are smooth (60fps)

## Sign-off

After completing all tests, document any issues found and verify fixes:

- [ ] Desktop layout tested and approved
- [ ] Tablet layout tested and approved
- [ ] Mobile layout tested and approved
- [ ] All breakpoint transitions work correctly
- [ ] Touch interactions work as expected
- [ ] No critical issues remaining

**Tested by**: _________________
**Date**: _________________
**Browser/Device**: _________________
**Notes**: _________________
