import React from 'react';
import { Modal as PaperModal, ModalProps, Portal } from 'react-native-paper';
import { useColorScheme } from '@/hooks/useColorScheme';
import { getComponentStyles } from './theme';

/**
 * StyledModal is a custom component for displaying content in a modal dialog.
 * It wraps React Native Paper's Modal component and provides a default style for the content area.
 *
 * @param {ModalProps} props - The props for the component.
 * @returns {React.ReactElement} The rendered modal component.
 *
 * @example
 * const [visible, setVisible] = React.useState(false);
 * const showModal = () => setVisible(true);
 * const hideModal = () => setVisible(false);
 *
 * return (
 *   <>
 *     <StyledModal visible={visible} onDismiss={hideModal}>
 *       <ThemedText>This is a modal!</ThemedText>
 *     </StyledModal>
 *     <StyledButton onPress={showModal}>Show Modal</StyledButton>
 *   </>
 * );
 *
 * @property {boolean} visible - Whether the modal is visible.
 * @property {() => void} onDismiss - Callback that is called when the user dismisses the modal.
 * @property {React.ReactNode} children - The content to be displayed inside the modal.
 * @property {StyleProp<ViewStyle>} [contentContainerStyle] - Style for the content container.
 */
const StyledModal: React.FC<ModalProps> = ({ children, style, contentContainerStyle, ...props }) => {
    const colorScheme = useColorScheme() ?? 'light';
    const styles = getComponentStyles(colorScheme);

    return (
        <Portal>
            <PaperModal
                contentContainerStyle={[styles.modalContent, contentContainerStyle]}
                {...props}
            >
                {children}
            </PaperModal>
        </Portal>
    );
};

export default StyledModal;
