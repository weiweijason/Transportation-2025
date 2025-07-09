import React from 'react';
import { ProgressBar as PaperProgressBar, ProgressBarProps } from 'react-native-paper';
import { useColorScheme } from '@/hooks/useColorScheme';
import { getComponentStyles } from './theme';
import { useThemeColor } from '@/hooks/useThemeColor';

/**
 * StyledProgressBar is a custom component for displaying progress.
 * It wraps React Native Paper's ProgressBar component.
 *
 * @param {ProgressBarProps} props - The props for the component.
 * @returns {React.ReactElement} The rendered progress bar component.
 *
 * @example
 * // A progress bar showing 50% completion
 * <StyledProgressBar progress={0.5} />
 *
 * @example
 * // A progress bar with a custom color and height
 * <StyledProgressBar progress={0.75} color="#ff0000" style={{ height: 10 }} />
 *
 * @property {number} progress - The progress of the bar, a value between 0 and 1.
 * @property {string} [color] - The color of the progress bar.
 * @property {boolean} [visible=true] - Whether the progress bar is visible.
 * @property {StyleProp<ViewStyle>} [style] - Custom styles to apply to the progress bar.
 */
const StyledProgressBar: React.FC<ProgressBarProps> = ({ color, ...props }) => {
    const colorScheme = useColorScheme() ?? 'light';
    const styles = getComponentStyles(colorScheme);
    const themeColor = useThemeColor({}, 'tint');

    return (
        <PaperProgressBar style={styles.progressBar} color={color || themeColor} {...props} />
    );
};

export default StyledProgressBar;
