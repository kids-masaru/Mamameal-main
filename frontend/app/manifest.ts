import { MetadataRoute } from 'next'

export default function manifest(): MetadataRoute.Manifest {
    return {
        name: 'Mamameal Works',
        short_name: 'Mamameal',
        description: 'Mamameal 業務効率化ツール',
        start_url: '/',
        display: 'standalone',
        background_color: '#ffffff',
        theme_color: '#f97316',
        icons: [
            {
                src: '/icon.jpg',
                sizes: '192x192',
                type: 'image/jpeg',
            },
            {
                src: '/icon.jpg',
                sizes: '512x512',
                type: 'image/jpeg',
            },
        ],
    }
}
