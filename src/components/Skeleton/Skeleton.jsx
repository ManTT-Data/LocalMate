import React from 'react';
import { Box } from '@mantine/core';

/**
 * Skeleton loading component with shimmer animation
 * Usage:
 * <Skeleton type="text" />
 * <Skeleton type="avatar" />
 * <Skeleton type="card" />
 * <Skeleton type="image" />
 */
const Skeleton = ({ type = 'text', width, height, className = '' }) => {
    const getTypeStyles = () => {
        switch (type) {
            case 'text':
                return 'skeleton skeleton-text';
            case 'text-sm':
                return 'skeleton skeleton-text skeleton-text-sm';
            case 'avatar':
                return 'skeleton skeleton-avatar';
            case 'card':
                return 'skeleton skeleton-card';
            case 'image':
                return 'skeleton skeleton-image';
            default:
                return 'skeleton';
        }
    };

    return (
        <Box
            className={`${getTypeStyles()} ${className}`}
            style={{
                width: width || undefined,
                height: height || undefined,
            }}
        />
    );
};

/**
 * Skeleton message loader for chat
 */
export const SkeletonMessage = () => (
    <Box style={{ display: 'flex', gap: '12px', padding: '16px 0' }}>
        <Skeleton type="avatar" />
        <Box style={{ flex: 1 }}>
            <Skeleton type="text" width="40%" />
            <Skeleton type="text" width="90%" />
            <Skeleton type="text-sm" width="60%" />
        </Box>
    </Box>
);

/**
 * Skeleton card loader for places
 */
export const SkeletonPlaceCard = () => (
    <Box
        className="skeleton-card"
        style={{
            padding: '16px',
            display: 'flex',
            gap: '12px',
            borderRadius: 'var(--radius-lg)',
        }}
    >
        <Skeleton type="image" width={80} height={80} style={{ borderRadius: 'var(--radius-md)' }} />
        <Box style={{ flex: 1 }}>
            <Skeleton type="text" width="70%" />
            <Skeleton type="text-sm" width="50%" />
            <Skeleton type="text-sm" width="30%" />
        </Box>
    </Box>
);

export default Skeleton;
