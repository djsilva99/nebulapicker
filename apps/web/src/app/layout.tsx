"use client";

import {
    ChakraProvider,
    defaultSystem,
    Grid,
    Box,
    Icon,
    Text,
    Heading,
    Image,
} from "@chakra-ui/react";
import NextLink from 'next/link';
import { FiGlobe, FiRss } from 'react-icons/fi';
import Head from "next/head";
import { IconType } from "react-icons";
import { useState, useEffect, useRef } from 'react';

interface SidebarLinkProps {
  href: string;
  icon: IconType;
  children: React.ReactNode;
}

const SidebarLink = ({ href, icon, children }: SidebarLinkProps) => (
  <NextLink href={href} passHref legacyBehavior>
    <Box
      as="a"
      p={3}
      borderRadius="md"
      _hover={{ bg: 'gray.700', color: '#AC7DBA' }}
      display="flex"
      alignItems="center"
      flexShrink={0}
      pl={{ base: 0, md: 10 }}
    >
      <Icon as={icon} mr={3} />
      <Text fontWeight="medium" display={{ base: 'block', md: 'block' }}>
        {children}
      </Text>
    </Box>
  </NextLink>
);

const ChakraRootLayoutContent = ({ children }: { children: React.ReactNode }) => {
  const [isVisible, setIsVisible] = useState(true);
  const lastScrollY = useRef(0);
  const MOBILE_HEADER_HEIGHT = '60px';

  return (
    <Grid
      templateColumns={{ base: '1fr', md: '200px 1fr' }}
      minH="100vh"
      bg="gray.900"
      color="white"
      alignContent="start"
    >

      {/* SIDEBAR / HEADER */}
      <Box
        bg="gray.800"
        p={{ base: 0, md: 4 }}
        borderRight={{ base: 'none', md: '0px solid' }}
        borderBottom={{ base: '1px solid', md: 'none' }}
        borderColor="gray.700"

        height={{ base: MOBILE_HEADER_HEIGHT, md: '100vh' }}
        overflow="visible"

        position="sticky"
        top="0"
        zIndex={{ base: 'sticky', md: 'base' }}

        transform={{
          base: isVisible ? 'translateY(0)' : 'translateY(-100%)',
          md: 'none',
        }}
        transition={{
          base: 'transform 0.3s ease-in-out',
          md: 'none',
        }}

        display={{ base: 'flex', md: 'block' }}
        flexDirection={{ base: 'row', md: 'column' }}
        alignItems={{ base: 'center', md: 'flex-start' }}
        justifyContent={{ base: 'space-between', md: 'flex-start' }}
        px={{ base: 4, md: 0 }}
      >

        {/* LOGO LINK */}
        <NextLink href="/" passHref legacyBehavior>
          <Box
            as="a"
            cursor="pointer"
            display="block"
            py={{ base: 0, md: 0 }}
          >
            <Heading
                as="h2"
                size={{ base: 'md', md: '2xl' }}
                color="white"
                display="flex"
                alignItems="center"
                gap={3}
                mb={{ base: 0, md: 6 }}
                ml={{ base: 0, md: 8 }}
            >
              <Image
                src="/nebulapicker.png"
                alt="Nebula Picker Logo"
                boxSize={{ base: '24px', md: '32px' }}
                objectFit="contain"
              />
                <Text fontSize={12} display={{ base: 'block', md: 'block' }}>
                  nebulapicker
                </Text>
            </Heading>
          </Box>
        </NextLink>

        {/* NAVIGATION LINKS CONTAINER */}
        <Box
          display="flex"
          flexDirection={{ base: 'row', md: 'column' }}
          gap={3}
          justifyContent={{ base: 'flex-end', md: 'flex-start' }}
          alignItems={{ base: 'center', md: 'stretch' }}
          mt={{ base: 0, md: 0 }}
          height={{ base: 'auto', md: 'auto' }}
          px={{ base: 0, md: 0 }}
        >
          <SidebarLink href="/sources" icon={FiGlobe}>
            Sources
          </SidebarLink>
          <SidebarLink href="/feeds" icon={FiRss}>
            Feeds
          </SidebarLink>
        </Box>
      </Box>

      {/* MAIN WINDOW */}
      <Box
        p={{ base: 3, md: 6 }}
        w="full"
        pt={{ base: MOBILE_HEADER_HEIGHT, md: 8 }}
      >
        {children}
      </Box>
    </Grid>
  );
};

export default function RootLayout(
  { children }: { children: React.ReactNode }
) {
  return (
    <html lang="en" style={{ backgroundColor: '#1a202c' }}>
      <Head>
        <title>nebulapicker</title>
        <link rel="icon" href="/favicon.ico" />
        <link rel="apple-touch-icon" sizes="180x180" href="/icons/icon-180.png" />
        <link rel="apple-touch-icon" sizes="152x152" href="/icons/icon-152.png" />
        <link rel="apple-touch-icon" sizes="120x120" href="/icons/icon-120.png" />
        <link rel="apple-touch-icon" href="/icons/icon-180.png" />
        <meta name="apple-mobile-web-app-capable" content="yes" />
        <meta name="apple-mobile-web-app-status-bar-style" content="default" />
      </Head>
      <body
        style={
          { backgroundColor: 'black', color: 'white', minHeight: '100vh', margin: 0, padding: 0 }
        }
      >
        <ChakraProvider value={defaultSystem}>
          <ChakraRootLayoutContent>
            {children}
          </ChakraRootLayoutContent>
        </ChakraProvider>
      </body>
    </html>
  );
}
