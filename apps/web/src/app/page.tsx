"use client";

import { Box, Heading, Text } from "@chakra-ui/react";
import { useEffect, useState } from "react";
import axios from "axios";

export default function Home() {
  const [data, setData] = useState<string | null>(null);

  const fetchData = async () => {
    try {
      const res = await axios.get("/api/v1/");
      setData(res.data.message);
    } catch (error) {
      console.error("Error fetching data:", error);
      setData("<p>Failed to load content.</p>");
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  const renderParagraphs = () => {
    if (!data) return null;
    const parser = new DOMParser();
    const doc = parser.parseFromString(data, "text/html");
    const paragraphs = Array.from(doc.querySelectorAll("p")).map((p) => p.innerHTML);

    return paragraphs.map((p, idx) => (
      <Text key={idx} mb={6} fontSize="md" lineHeight="tall">
        <span dangerouslySetInnerHTML={{ __html: p }} />
      </Text>
    ));
  };

  return (
    <Box p={8} textAlign="center">
      <Heading mb={4}>NebulaPicker v1.0</Heading>

      <Box textAlign="left">{renderParagraphs()}</Box>

      <Box flex="1" minH="calc(100vh - 200px)" />
    </Box>
  );
}
