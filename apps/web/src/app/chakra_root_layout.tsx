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


export const ChakraRootLayout = ({ children }: { children: React.ReactNode }) => {
  const [isVisible, setIsVisible] = useState(true);
  const MOBILE_HEADER_HEIGHT = '60px';

  return (
    <ChakraProvider value={defaultSystem}>
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
              mt="0"
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
          maxWidth={1250}
          justifySelf="center"
        >
          {children}
        </Box>
      </Grid>
    </ChakraProvider>
  );
};
