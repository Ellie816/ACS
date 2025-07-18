import React, { useEffect, useState } from 'react';
import { Artist } from '../types/Artist';

const ArtistTable: React.FC = () => {
    const [artists, setArtists] = useState<Artist[]>([]);
    const [loading, setLoading] = useState<boolean>(true);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        const fetchArtists = async () => {
            try {
                const response = await fetch('/api/artists'); // Adjust the API endpoint as needed
                if (!response.ok) {
                    throw new Error('Network response was not ok');
                }
                const data = await response.json();
                setArtists(data);
            } catch (error) {
                setError(error.message);
            } finally {
                setLoading(false);
            }
        };

        fetchArtists();
    }, []);

    if (loading) {
        return <div>Loading...</div>;
    }

    if (error) {
        return <div>Error: {error}</div>;
    }

    return (
        <table>
            <thead>
                <tr>
                    <th>Artist Name</th>
                    <th>Title</th>
                    <th>Estimate</th>
                    <th>Lot Number</th>
                    <th>Collecting Society</th>
                    <th>Resale Right</th>
                </tr>
            </thead>
            <tbody>
                {artists.map((artist) => (
                    <tr key={artist.lot_number}>
                        <td>{artist.artist_name}</td>
                        <td>{artist.title}</td>
                        <td>{artist.estimate}</td>
                        <td>{artist.lot_number}</td>
                        <td>{artist.collecting_society || 'N/A'}</td>
                        <td>{artist.resale_right}</td>
                    </tr>
                ))}
            </tbody>
        </table>
    );
};

export default ArtistTable;