import React, { useState } from 'react';
import { View, StyleSheet, ScrollView } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import StyledCard from '@/components/basic/StyledCard';
import StyledButton from '@/components/basic/StyledButton';
import { ThemedText } from '@/components/ThemedText';
import StyledInput from '@/components/basic/StyledInput';
import StyledProgressBar from '@/components/basic/StyledProgressBar';
import StyledModal from '@/components/basic/StyledModal';
import StyledSpinner from '@/components/basic/StyledSpinner';
import StyledAvatar from '@/components/basic/StyledAvatar';
import StyledBadge from '@/components/basic/StyledBadge';
import StyledIcon from '@/components/basic/StyledIcon';

export default function ComponentExamplesScreen() {
    const [modalVisible, setModalVisible] = useState(false);

    return (
        <SafeAreaView style={{ flex: 1 }}>
            <ScrollView contentContainerStyle={styles.container}>
                <ThemedText type="title">Component Examples</ThemedText>

                {/* Input Examples */}
                <ThemedText type="subtitle">Inputs</ThemedText>
                <StyledInput label="Email" />
                <StyledInput label="Password" secureTextEntry />

                {/* ProgressBar Example */}
                <ThemedText type="subtitle">Progress Bar</ThemedText>
                <StyledProgressBar progress={0.7} />

                {/* Modal Example */}
                <ThemedText type="subtitle">Modal</ThemedText>
                <StyledButton onPress={() => setModalVisible(true)}>Show Modal</StyledButton>
                <StyledModal visible={modalVisible} onDismiss={() => setModalVisible(false)}>
                    <ThemedText>This is a modal!</ThemedText>
                    <StyledButton onPress={() => setModalVisible(false)} style={{ marginTop: 10 }}>Close</StyledButton>
                </StyledModal>

                {/* Spinner Example */}
                <ThemedText type="subtitle">Spinner</ThemedText>
                <StyledSpinner />

                {/* Avatar Example */}
                <ThemedText type="subtitle">Avatar</ThemedText>
                <View style={styles.row}>
                    <StyledAvatar source={{ uri: 'https://picsum.photos/80' }} size={80} />
                    <StyledAvatar source={require('@/assets/images/icon.png')} size={100} level={5} />
                </View>

                {/* Badge Example */}
                <ThemedText type="subtitle">Badge</ThemedText>
                <View style={styles.row}>
                    <StyledBadge>SR</StyledBadge>
                    <StyledBadge>SSR</StyledBadge>
                </View>

                {/* Icon Example */}
                <ThemedText type="subtitle">Icon</ThemedText>
                <View style={styles.row}>
                    <StyledIcon name="camera" size={30} />
                    <StyledIcon name="heart" size={30} />
                </View>

                {/* Card Examples */}
                <ThemedText type="subtitle">Cards</ThemedText>
                <StyledCard>
                    <StyledCard.Content>
                        <ThemedText>This is a simple card.</ThemedText>
                    </StyledCard.Content>
                </StyledCard>

                <StyledCard>
                    <StyledCard.Title title="Creature Info" subtitle="Fire - Rare" />
                    <StyledCard.Content>
                        <ThemedText>A powerful fire creature.</ThemedText>
                    </StyledCard.Content>
                    <StyledCard.Actions>
                        <StyledButton mode="text">Details</StyledButton>
                        <StyledButton mode="contained">Catch</StyledButton>
                    </StyledCard.Actions>
                </StyledCard>
            </ScrollView>
        </SafeAreaView>
    );
}

const styles = StyleSheet.create({
    container: {
        padding: 16,
        paddingBottom: 50, // Add padding to the bottom
        gap: 20,
    },
    row: {
        flexDirection: 'row',
        alignItems: 'center',
        gap: 10,
    },
});
