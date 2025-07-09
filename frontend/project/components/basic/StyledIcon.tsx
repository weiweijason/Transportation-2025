import React from 'react';
import { Icon as PaperIcon, IconProps } from 'react-native-paper';
import { useThemeColor } from '@/hooks/useThemeColor';

// Define the props for our custom icon, extending the original IconProps
interface StyledIconProps extends Omit<IconProps, 'source'> {
  /** The name of the icon to display from MaterialCommunityIcons. */
  name: string;
}

/**
 * StyledIcon is a custom component for displaying icons.
 * It wraps React Native Paper's Icon component and sets MaterialCommunityIcons as the default source.
 * Find all available icons at https://icons.expo.fyi/
 *
 * @param {StyledIconProps} props - The props for the component.
 * @returns {React.ReactElement} The rendered icon component.
 *
 * @example
 * // A simple icon with default size and color
 * <StyledIcon name="camera" />
 *
 * @example
 * // An icon with a specific size and color
 * <StyledIcon name="heart" size={48} color="#e74c3c" />
 *
 * @property {string} name - The name of the icon to display.
 * @property {number} [size=24] - The size of the icon.
 * @property {string} [color] - The color of the icon.
 */
const StyledIcon: React.FC<StyledIconProps> = ({ name, color, ...props }) => {
  const themeColor = useThemeColor({}, 'icon');

  return <PaperIcon source={name} color={color || themeColor} {...props} />;
};

export default StyledIcon;
