import { StyleSheet } from 'react-native';
import { Colors } from '@/constants/Colors';

export const getComponentStyles = (colorScheme: 'light' | 'dark') => {
    const themeColors = Colors[colorScheme];

    return StyleSheet.create({
        // StyledAvatar
        avatarBadge: {
            position: 'absolute',
            right: 0,
            bottom: 0,
            backgroundColor: themeColors.tint,
            borderWidth: 2,
            borderColor: themeColors.background,
        },
        // StyledBadge
        badge: {
            fontWeight: 'bold',
        },
        // StyledButton
        button: {
            borderRadius: 20,
            paddingVertical: 6,
            paddingHorizontal: 12,
        },
        buttonLabel: {
            fontWeight: 'bold',
        },
        // StyledCard
        card: {
            borderRadius: 15,
            marginHorizontal: 0, // Use marginVertical or rely on parent container gap
            marginVertical: 0,
            elevation: 4,
            backgroundColor: themeColors.background,
            shadowColor: '#000',
            shadowOffset: { width: 0, height: 2 },
            shadowOpacity: colorScheme === 'light' ? 0.1 : 0.3,
            shadowRadius: 4,
            borderWidth: colorScheme === 'dark' ? 1 : 0,
            borderColor: colorScheme === 'dark' ? themeColors.icon : 'transparent',
        },
        cardPressed: {
            transform: [{ translateY: -5 }],
            shadowOpacity: colorScheme === 'light' ? 0.2 : 0.5,
            elevation: 8,
        },
        // StyledInput
        input: {
            marginBottom: 16,
            backgroundColor: themeColors.background,
        },
        // StyledModal
        modalContent: {
            backgroundColor: themeColors.background,
            padding: 22,
            margin: 20,
            borderRadius: 15,
            borderColor: colorScheme === 'dark' ? themeColors.icon : 'transparent',
            borderWidth: 1,
        },
        // StyledProgressBar
        progressBar: {
            borderRadius: 5,
            height: 8,
        },
    });
};
