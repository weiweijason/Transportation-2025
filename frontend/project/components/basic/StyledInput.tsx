import React from 'react';
import { TextInput as PaperInput, TextInputProps } from 'react-native-paper';
import { useColorScheme } from '@/hooks/useColorScheme';
import { getComponentStyles } from './theme';

/**
 * StyledInput is a custom component for text input fields.
 * It wraps React Native Paper's TextInput component and provides a default style.
 *
 * @param {TextInputProps} props - The props for the component.
 * @returns {React.ReactElement} The rendered input component.
 *
 * @example
 * // A simple text input with a label
 * <StyledInput label="Email" />
 *
 * @example
 * // A secure text input for passwords
 * <StyledInput label="Password" secureTextEntry />
 *
 * @example
 * // An outlined input with an icon
 * <StyledInput
 *   label="Username"
 *   mode="outlined"
 *   left={<PaperInput.Icon icon="account" />}
 * />
 */
const StyledInput: React.FC<TextInputProps> = (props) => {
    const colorScheme = useColorScheme() ?? 'light';
    const styles = getComponentStyles(colorScheme);

    return (
        <PaperInput
            style={[styles.input, props.style]}
            {...props}
        />
    );
};

export default StyledInput;
