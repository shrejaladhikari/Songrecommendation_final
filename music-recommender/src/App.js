import React, { useState, useEffect } from "react";

const App = () => {
  const [selectedSong, setSelectedSong] = useState(""); // User-selected song
  const [recommendations, setRecommendations] = useState([]); // Recommended songs
  const [posters, setPosters] = useState([]); // Album covers
  const [songList, setSongList] = useState([]); // List of all songs
  const [loading, setLoading] = useState(false); // Loading state for fetching songs or recommendations
  const [message, setMessage] = useState(
    "Choose any song from below to see which songs are similar to yours."
  ); // Instructional message

  // Fetch all songs from the backend on component mount
  useEffect(() => {
    const fetchSongs = async () => {
      try {
        setLoading(true); // Start loading
        const response = await fetch("http://127.0.0.1:5000/songs");
        const data = await response.json();
        setSongList(data.songs);
      } catch (error) {
        console.error("Error fetching songs:", error);
      } finally {
        setLoading(false); // Stop loading
      }
    };

    fetchSongs();
  }, []);

  const fetchRecommendations = async () => {
    try {
      setLoading(true);

      if (!selectedSong) {
        alert("Please select a song!");
        setLoading(false);
        return;
      }

      const response = await fetch("http://127.0.0.1:5000/recommend", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ song: selectedSong }),
      });

      if (!response.ok) throw new Error("Failed to fetch recommendations");

      const data = await response.json();
      setRecommendations(data.songs);
      setPosters(data.posters);

      if (data.songs.length === 0) {
        setMessage("No recommendations found for the selected song.");
      } else {
        setMessage("Here are the songs tailored for you:");
      }
    } catch (error) {
      console.error("Error fetching recommendations:", error);
      setMessage("An error occurred while fetching recommendations.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-800 text-white p-10">
      <h1 className="text-4xl font-bold text-center">Music Recommender</h1>
      <div className="mt-4 text-center text-lg">{message}</div>
      <div className="mt-8 flex flex-col items-center">
        <select
          className="p-3 rounded bg-gray-700"
          value={selectedSong}
          onChange={(e) => setSelectedSong(e.target.value)}
        >
          <option value="">Select a song</option>
          {songList.map((song, index) => (
            <option key={index} value={song}>
              {song}
            </option>
          ))}
        </select>

        {/* Animated Loading Button */}
        <button
          onClick={fetchRecommendations}
          className={`mt-4 text-white py-2 px-4 rounded ${
            loading ? "bg-blue-300 cursor-not-allowed" : "bg-blue-500 hover:bg-blue-600"
          }`}
          disabled={loading}
        >
          {loading ? (
            <div className="flex items-center">
              <div className="loader-button mr-2"></div> Loading...
            </div>
          ) : (
            "Get Recommendations"
          )}
        </button>
      </div>

      {/* Recommendations Section */}
      <div className="mt-8 grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-6">
        {recommendations.map((song, index) => (
          <div key={index} className="bg-gray-700 p-4 rounded">
            <img
              src={posters[index]}
              alt={song}
              className="w-full h-40 object-cover rounded"
            />
            <h3 className="mt-2 text-center text-lg">{song}</h3>
          </div>
        ))}
      </div>
    </div>
  );
};

export default App;