"use client";

import {
  Table,
  Heading,
  Box,
  Flex,
} from "@chakra-ui/react";
import { useState, useEffect } from "react";
import axios from "axios";
import { Feed, FeedItem } from "@/types/Feed";
import { useParams } from 'next/navigation';


const normalizeUrl = (url: string) => {
  if (!url.startsWith("http://") && !url.startsWith("https://")) {
    return "https://" + url;
  }
  return url;
};

function timeDeltaFromNow(dateString: string): string {
  const now = new Date();
  const date = new Date(dateString);
  const diffMs = now.getTime() - date.getTime();

  if (diffMs < 0) return "0m";

  const seconds = Math.floor(diffMs / 1000);
  const minutes = Math.floor(seconds / 60);
  const hours = Math.floor(minutes / 60);
  const days = Math.floor(hours / 24);
  const weeks = Math.floor(days / 7);

  if (weeks > 0) return `${weeks}w`;
  if (days > 0) return `${days}d`;
  if (hours > 0) return `${hours}h`;
  if (minutes > 0) return `${minutes}m`;
  return `${seconds}s`;
}


export default function FeedPage() {
  const params = useParams();
  const feedId = params.feed_id as string;

  const [data, setData] = useState<Feed>();
  const [isLoading, setIsLoading] = useState(true);

  const fetchData = async () => {
    setIsLoading(true);
    try {
      const feedRes = await axios.get("/api/v1/feeds/" + feedId);
      setData(feedRes.data);
    } catch (error) {
      console.error("Error fetching data:", error);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, [feedId]);

  if (isLoading) {
    return (
      <Box p={6}>
        <Heading as="h1" size="xl" mb={6}>Feeds</Heading>
        <p>Loading feed items...</p>
      </Box>
    );
  }

  return (
    <Box p={6}>

      {/* HEADER */}
      <Flex
        justifyContent="space-between"
        alignItems="center"
        mb={6}
      >
        <Heading as="h1" size="xl">
          {data?.name} ({data?.feed_items?.length})
        </Heading>
      </Flex>

      {/* TABLE */}
      <Table.Root size="sm" variant="outline">
        <Table.ColumnGroup>
          <Table.Column htmlWidth="80%" />
          <Table.Column htmlWidth="15%" />
          <Table.Column htmlWidth="5%" />
        </Table.ColumnGroup>
        <Table.Header>
          <Table.Row>
            <Table.ColumnHeader bg="gray.700" color='white'>TITLE</Table.ColumnHeader>
            <Table.ColumnHeader bg="gray.700" color='white'>AUTHOR</Table.ColumnHeader>
            <Table.ColumnHeader bg="gray.700" color='white'>DATE</Table.ColumnHeader>
          </Table.Row>
        </Table.Header>

        <Table.Body>
        {data?.feed_items?.slice().sort(
            (a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime()
        ).map((item: FeedItem) => (
          <Table.Row
            key={item.external_id}
            cursor="pointer"
            color="gray.400"
            _hover={{ bg: 'gray.800', color: '#AC7DBA' }}
          >
            <Table.Cell borderLeft="none" borderRight="none">
              <a
                href={normalizeUrl(item.link)}
                target="_blank"
                rel="noopener noreferrer"
              >
                <Box>{item.title}</Box>
              </a>
            </Table.Cell>
            <Table.Cell borderLeft="none" borderRight="none">
              <a href={normalizeUrl(item.link)}
                target="_blank"
                rel="noopener noreferrer"
              >
                <Box>{item.author}</Box>
              </a>
            </Table.Cell>
            <Table.Cell borderLeft="none" borderRight="none">
              <a
                href={normalizeUrl(item.link)}
                target="_blank"
                rel="noopener noreferrer"
              >
                <Box>{timeDeltaFromNow(item.created_at)}</Box>
              </a>
            </Table.Cell>
          </Table.Row>
        ))}
        </Table.Body>
      </Table.Root>
    </Box>
  )
}
