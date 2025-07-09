import React from 'react';
import { Button as PaperButton, ButtonProps } from 'react-native-paper';
import { useColorScheme } from '@/hooks/useColorScheme';
import { getComponentStyles } from './theme';

// Define the props for our custom button, extending the original ButtonProps
interface StyledButtonProps extends ButtonProps {
    // You can add custom props here if needed
}

/**
 * StyledButton is a custom button component that wraps React Native Paper's Button.
 * It provides a consistent style for buttons across the application.
 *
 * @param {StyledButtonProps} props - The props for the component.
 * @returns {React.ReactElement} The rendered button component.
 *
 * @example
 * // Contained button (for primary actions)
 * <StyledButton mode="contained" onPress={() => console.log('Pressed')}>
 *   Press me
 * </StyledButton>
 *
 * @example
 * // Outlined button (for secondary actions)
 * <StyledButton mode="outlined" icon="camera" onPress={() => console.log('Pressed')}>
 *   Press me
 * </StyledButton>
 *
 * @example
 * // Text button (for low-priority actions)
 * <StyledButton mode="text" onPress={() => console.log('Pressed')}>
 *   Press me
 * </StyledButton>
 *
 * @property {string} mode - The mode of the button. Can be 'text', 'outlined', or 'contained'.
 *    - `contained`: A solid button for primary actions.
 *    - `outlined`: A button with an outline for secondary actions.
 *    - `text`: A flat button for low-priority actions.
 * @property {() => void} onPress - Function to execute on press.
 * @property {React.ReactNode} children - The content of the button.
 * @property {string} [icon] - The name of the icon. see https://icons.expo.fyi/
 * @property {boolean} [disabled] - Whether the button is disabled.
 * @property {StyleProp<ViewStyle>} [style] - Custom styles to apply to the button.
 */
const StyledButton: React.FC<StyledButtonProps> = ({ children, style, ...props }) => {
    const colorScheme = useColorScheme() ?? 'light';
    const styles = getComponentStyles(colorScheme);

    return (
        <PaperButton
            style={[styles.button, style]} // Apply default styles and allow overriding
            labelStyle={styles.buttonLabel}
            {...props}
        >
            {children}
        </PaperButton>
    );
};

export default StyledButton;
