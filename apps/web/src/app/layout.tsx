"use client";

import {
  ChakraProvider,
  defaultSystem,
  Grid,
  Box,
  Icon,
  Text,
  Heading,
  Image
} from "@chakra-ui/react";
import NextLink from 'next/link';
import { FiGlobe, FiRss } from 'react-icons/fi';
import Head from "next/head";
import { IconType } from "react-icons";

export default function RootLayout(
  { children }: { children: React.ReactNode }
) {

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
        w="full"
        borderRadius="md"
        _hover={{ bg: 'gray.700', color: '#AC7DBA' }}
        display="flex"
        alignItems="center"
      >
        <Icon as={icon} mr={3} />
        <Text fontWeight="medium">{children}</Text>
      </Box>
    </NextLink>
  );

  return (
    <html lang="en" style={{ backgroundColor: '#1a202c' }}>
      <Head>
        <title>nebulapicker</title>
        <link rel="icon" href="/favicon.ico" />
      </Head>
      <body
        style={
          { backgroundColor: 'black', color: 'white', minHeight: '100vh' }
        }
      >
        <ChakraProvider value={defaultSystem}>
          <Grid
            templateColumns="250px 1fr"
            minH="100vh"
            bg="gray.900"
            color="white"
          >
            {/* SIDEBAR */}
            <Box
              bg="gray.800"
              p={4}
              borderRight="1px solid"
              borderColor="gray.700"
            >
              <NextLink href="/" passHref legacyBehavior>
                <Box
                  as="a"
                  cursor="pointer"
                  display="block"
                  mb={6}
                >
                  <Heading
                    as="h2"
                    size="2xl"
                    color="white"
                    display="flex"
                    alignItems="center"
                    gap={3}
                    mb={6}
                  >
                    <Image
                      src="/nebulapicker.png"
                      alt="Nebula Picker Logo"
                      boxSize="32px"
                      objectFit="contain"
                    />
                    nebulapicker
                  </Heading>
                </Box>
              </NextLink>
              <SidebarLink href="/sources" icon={FiGlobe}>
                Sources
              </SidebarLink>
              <SidebarLink href="/feeds" icon={FiRss}>
                Feeds
              </SidebarLink>
            </Box>

            {/* MAIN WINDOW */}
            <Box p={8}>
              {children}
            </Box>
          </Grid>
        </ChakraProvider>
      </body>
    </html>
  );
}
