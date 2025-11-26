"use client";

import { useState } from "react";
import Cookies from "js-cookie";
import {
  Button,
  Input,
  Box,
  Heading,
  VStack,
} from "@chakra-ui/react";
import {
  FormControl,
  FormLabel
} from "@chakra-ui/form-control";
import { useToast } from "@chakra-ui/toast";

export default function LoginPage() {
  const toast = useToast();

  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);

  async function handleLogin() {
    setLoading(true);

    try {
      const res = await fetch("/api/v1/login", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ username, password }),
      });

      if (!res.ok) {
        toast({
          title: "Invalid credentials",
          status: "error",
          duration: 3000,
          isClosable: true,
        });
        setLoading(false);
        return;
      }

      const data = await res.json();

      Cookies.set("token", data.token);

      toast({
        title: "Login successful",
        status: "success",
        duration: 2000,
        isClosable: true,
      });

      window.location.href = "/feeds";
    } catch (err) {
      toast({
        title: "Login error",
        status: "error",
        duration: 3000,
        isClosable: true,
      });
      console.error(err);
    } finally {
      setLoading(false);
    }
  }

  return (
    <Box
      maxW="400px"
      mx="auto"
      mt="100px"
      p={6}
      borderRadius="lg"
      boxShadow="md"
    >
      <Heading textAlign="center" mb={6}>
        Login
      </Heading>

      <VStack>
        <FormControl>
          <FormLabel>Username</FormLabel>
          <Input
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            placeholder="Enter username"
          />
        </FormControl>

        <FormControl>
          <FormLabel>Password</FormLabel>
          <Input
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            placeholder="Enter password"
          />
        </FormControl>

        <Button
          width="100%"
          colorScheme="blue"
          onClick={handleLogin}
          loading={loading}
        >
          Login
        </Button>
      </VStack>
      <Box flex="1" minH="calc(100vh - 200px)" />
    </Box>
  );
}
