import React from 'react';
import { View } from 'react-native';
import { Avatar as PaperAvatar, Badge } from 'react-native-paper';
import { useColorScheme } from '@/hooks/useColorScheme';
import { getComponentStyles } from './theme';

interface StyledAvatarProps {
    /** The source for the image. Can be a local require() or a remote URI. */
    source: any;
    /** The size of the avatar. */
    size?: number;
    /** The level or number to display in the badge. If not provided, no badge will be shown. */
    level?: number;
}

/**
 * StyledAvatar is a custom component that displays a user or character avatar.
 * It wraps React Native Paper's Avatar.Image and adds an optional level badge.
 *
 * @param {StyledAvatarProps} props - The props for the component.
 * @returns {React.ReactElement} The rendered avatar component.
 *
 * @example
 * // Simple avatar
 * <StyledAvatar source={{ uri: 'https://example.com/avatar.png' }} size={80} />
 *
 * @example
 * // Avatar with a level badge at the bottom right
 * <StyledAvatar source={require('../assets/images/creature.png')} size={100} level={5} />
 */
const StyledAvatar: React.FC<StyledAvatarProps> = ({ source, size = 80, level }) => {
    const colorScheme = useColorScheme() ?? 'light';
    const styles = getComponentStyles(colorScheme);

    return (
        <View style={{ width: size, height: size }}>
            <PaperAvatar.Image size={size} source={source} />
            {level !== undefined && (
                <Badge style={[styles.avatarBadge, { transform: [{ translateX: size * 0.35 }, { translateY: size * -0.35 }] }]} size={size * 0.3}>
                    {level}
                </Badge>
            )}
        </View>
    );
};

export default StyledAvatar;
