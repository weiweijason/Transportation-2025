
import React from 'react';
import { Badge as PaperBadge, BadgeProps } from 'react-native-paper';
import { useColorScheme } from '@/hooks/useColorScheme';
import { getComponentStyles } from './theme';

// Define the props for our custom badge, extending the original BadgeProps
interface StyledBadgeProps extends BadgeProps {
    // You can add custom props here if needed
}

/**
 * StyledBadge is a custom component for displaying short status descriptors or notifications.
 * It wraps React Native Paper's Badge component.
 *
 * @param {StyledBadgeProps} props - The props for the component.
 * @returns {React.ReactElement} The rendered badge component.
 *
 * @example
 * // A simple badge with a number
 * <StyledBadge>3</StyledBadge>
 *
 * @example
 * // A larger badge with custom color
 * <StyledBadge size={30} style={{ backgroundColor: '#28a745' }}>
 *   SSR
 * </StyledBadge>
 *
 * @property {React.ReactNode} children - The content of the badge (usually a number or short text).
 * @property {number} [size=20] - The size of the badge.
 * @property {StyleProp<ViewStyle>} [style] - Custom styles to apply to the badge.
 */
const StyledBadge: React.FC<StyledBadgeProps> = ({ children, style, ...props }) => {
    const colorScheme = useColorScheme() ?? 'light';
    const styles = getComponentStyles(colorScheme);

    return (
        <PaperBadge style={[styles.badge, style]} {...props}>
            {children}
        </PaperBadge>
    );
};

export default StyledBadge;
