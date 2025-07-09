import React from 'react';
import { ActivityIndicator as PaperActivityIndicator, ActivityIndicatorProps } from 'react-native-paper';
import { useThemeColor } from '@/hooks/useThemeColor';

/**
 * StyledSpinner is a custom component for displaying a loading indicator.
 * It wraps React Native Paper's ActivityIndicator component.
 *
 * @param {ActivityIndicatorProps} props - The props for the component.
 * @returns {React.ReactElement} The rendered spinner component.
 *
 * @example
 * // A default spinner
 * <StyledSpinner />
 *
 * @example
 * // A large red spinner
 * <StyledSpinner size="large" color="#ff0000" />
 *
 * @property {'small' | 'large'} [size='small'] - The size of the spinner.
 * @property {string} [color] - The color of the spinner.
 * @property {boolean} [animating=true] - Whether to show the indicator or hide it.
 */
const StyledSpinner: React.FC<ActivityIndicatorProps> = ({ color, ...props }) => {
    const themeColor = useThemeColor({}, 'tint');

    return (
        <PaperActivityIndicator color={color || themeColor} {...props} />
    );
};

export default StyledSpinner;
