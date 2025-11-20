"use client";

import {
  Heading,
  Box,
  Link
} from "@chakra-ui/react";
import { useState, useEffect } from "react";
import axios from "axios";
import { FeedItem } from "@/types/Feed";
import { useParams } from 'next/navigation';
import { FiGlobe, FiArrowLeft, FiClock, FiCalendar } from "react-icons/fi";
import { useToast } from "@chakra-ui/toast";
import { Global } from "@emotion/react";

export default function FeedItemPage() {
  const params = useParams();
  const feedId = params.feed_id as string;
  const feedItemId = params.feed_item_id as string;

  const [data, setData] = useState<FeedItem>();
  const [feed, setFeed] = useState()
  const [isLoading, setIsLoading] = useState(true);

  const fetchData = async () => {
    setIsLoading(true);
    try {
      const feedRes = await axios.get("/api/v1/feeds/" + feedId + "/feed_items/" + feedItemId);
      setData(feedRes.data);
    } catch (error) {
      console.error("Error fetching data:", error);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, [feedItemId]);

  const fetchFeed = async () => {
    try {
      const feedRes = await axios.get("/api/v1/feeds/" + feedId);
      setFeed(feedRes.data.name);
    } catch (error) {
      console.error("Error fetching data:", error);
    } finally {
    }
  };

  useEffect(() => {
    fetchFeed();
  }, [feedId]);

  if (isLoading) {
    return (
      <Box p={6}>
        <Heading as="h1" size="xl" mb={6}>Feeds</Heading>
        <p>Loading feed item...</p>
      </Box>
    );
  }

  return (

    <Box p={1}>
      <Box maxW="800px" mx="auto">
        <Global
          styles={`
            .article-container {
                font-size: 1.15rem !important;
                line-height: 1.7 !important;
                font-weight: normal !important;
            }
            .article-container figure {
                page-break-inside: avoid !important;
                break-inside: avoid !important;
                page-break-before: auto !important;
                page-break-after: auto !important;
                margin: 1em auto !important;
                text-align: center !important;
                font-weight: normal !important;
                width: 100% !important;
                max-width: 100% !important;
            }

            .article-container figcaption {
                font-style: italic !important;
                font-size: 1em !important;
                text-align: center !important;
                margin-bottom: 1em !important;
                display: block;
                width: 100%;
                font-weight: normal !important;
            }

            .article-container p {
                margin-bottom: 1em !important;
                line-height: 1.7 !important;
                text-align: justify !important;
                font-size: 1.15rem !important;
                font-weight: normal !important;
            }

            .article-container div {
                margin-bottom: 1em !important;
                font-weight: normal !important;
            }

            .h1 {
                font-size: 2rem !important;
                font-weight: bold !important;
                margin-bottom: 0.6em !important;
                line-height: 1.3 !important;
                color: #7DCDE8 !important;
            }
          `}
        />
        <Box
          className="h1"
          dangerouslySetInnerHTML={{ __html: data?.title || "" }}
        />
        <Box>
          <Link href={`/feeds/${feedId}`} style={{ color: '#52525b' }}>
            <FiArrowLeft />
            {feed} feed
          </Link>

          <div
              style={{ display: "inline-flex", alignItems: "center", gap: "4px", marginLeft: "20px", color: '#52525b' }}
          >
              <FiClock />
              {data?.reading_time}m
          </div>

          <div
            style={{ display: "inline-flex", alignItems: "center", gap: "4px", marginLeft: "20px", color: '#52525b' }}
          >
            <FiCalendar />
            {data?.created_at.slice(0, 10)}
          </div>

          <div
            style={{ display: "inline-flex", alignItems: "center", gap: "4px", marginLeft: "20px", color: '#52525b' }}
          >
            <a
              href={data?.link}
              target="_blank"
              rel="noopener noreferrer"
              style={{ display: "inline-flex", alignItems: "center", gap: "4px"}}
            >
              <FiGlobe />
              {data?.author}
            </a>
          </div>
        </Box>
        <Box
          className="article-container"
          dangerouslySetInnerHTML={{ __html: data?.content || "" }}
        />
      </Box>
    </Box>
  )
}
