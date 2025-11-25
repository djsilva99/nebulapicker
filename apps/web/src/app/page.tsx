"use client";

import { Box, Heading, Text } from "@chakra-ui/react";
import { useState } from "react";
import axios from "axios";

export default function Home() {
  const [data, setData] = useState<string | null>(null);

  const fetchData = async () => {
    const res = await axios.get("/api/v1/");
    setData(JSON.stringify(res.data.message, null, 2));
  };

  console.log(fetchData())

  return (
    <Box p={8} textAlign="center">
      <Heading mb={4}>nebulapicker v1.0</Heading>
      <Text mb={4}>{data}</Text>
      <Box flex="1" minH="calc(100vh - 200px)" />
    </Box>
  );
}
