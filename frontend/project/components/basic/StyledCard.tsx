import React from 'react';
import { Pressable, ViewStyle } from 'react-native';
import { Card as PaperCard, CardProps } from 'react-native-paper';
import { useColorScheme } from '@/hooks/useColorScheme';
import { getComponentStyles } from './theme';

// Define the props for our custom card, extending the original CardProps
interface StyledCardProps extends CardProps {
  // You can add custom props here if needed
}

/**
 * StyledCard is a custom component for displaying content in a card format.
 * It wraps React Native Paper's Card component and provides a default style.
 *
 * @param {StyledCardProps} props - The props for the component.
 * @returns {React.ReactElement} The rendered card component.
 *
 * @example
 * <StyledCard onPress={() => console.log('Card pressed')}>
 *   <StyledCard.Title title="Card Title" subtitle="Card Subtitle" />
 *   <StyledCard.Content>
 *     <ThemedText>This is the card content.</ThemedText>
 *   </StyledCard.Content>
 * </StyledCard>
 */
const StyledCard: React.FC<StyledCardProps> & {
  Actions: typeof PaperCard.Actions;
  Content: typeof PaperCard.Content;
  Cover: typeof PaperCard.Cover;
  Title: typeof PaperCard.Title;
} = ({ children, style, onPress, mode = 'elevated', ...props }) => {
  const colorScheme = useColorScheme() ?? 'light';
  const styles = getComponentStyles(colorScheme);

  const isElevated = mode === 'elevated';

  const cardStyle: ViewStyle[] = [styles.card, style as ViewStyle];

  if (!isElevated) {
    // For non-elevated cards, remove elevation-related styles to prevent type errors
    delete cardStyle[0].elevation;
  }

  return (
    <Pressable onPress={onPress} disabled={!onPress}>
      {({ pressed }) => (
        <PaperCard
          style={[...cardStyle, isElevated && pressed && styles.cardPressed]}
          mode={mode}
          {...props}
        >
          {children}
        </PaperCard>
      )}
    </Pressable>
  );
};

// Expose sub-components from Paper.Card
StyledCard.Actions = PaperCard.Actions;
StyledCard.Content = PaperCard.Content;
StyledCard.Cover = PaperCard.Cover;
StyledCard.Title = PaperCard.Title;

export default StyledCard;
