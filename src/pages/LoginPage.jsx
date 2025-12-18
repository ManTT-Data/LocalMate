import React, { useState } from "react";
import { Title, Text, Button, Alert, Loader, Box } from "@mantine/core";
import { IconBrandGoogle, IconAlertCircle } from "@tabler/icons-react";
import { useNavigate } from "react-router-dom";
import { loginWithGoogleAPI } from "../apis/authService";
import { googlClientId } from "../utils/constants";
import useUserStore from "../stores/useUserStore";

const LoginPage = () => {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const setUser = useUserStore((state) => state.setUser);

  const handleGoogleLogin = () => {
    setLoading(true);
    setError(null);

    if (window.google) {
      const client = window.google.accounts.oauth2.initTokenClient({
        client_id: googlClientId,
        scope: "openid profile email",
        callback: async (response) => {
          try {
            if (response.access_token) {
              const loginResponse = await loginWithGoogleAPI(
                response.access_token
              );
              console.log("Login successful:", loginResponse);

              // Save user data to Zustand store
              setUser({
                id: loginResponse.user_id,
                email: loginResponse.email,
                name: loginResponse.full_name,
                avatar: loginResponse.avatar_url,
              });

              navigate("/map");
            } else {
              setError("Failed to get access token from Google");
              setLoading(false);
            }
          } catch (err) {
            console.error("Login error:", err);
            setError(err.message || "Login failed. Please try again.");
            setLoading(false);
          }
        },
        error_callback: (error) => {
          console.error("Google OAuth error:", error);
          setError("Google authentication failed. Please try again.");
          setLoading(false);
        },
      });

      client.requestAccessToken();
    } else {
      setError("Google Identity Services not loaded");
      setLoading(false);
    }
  };

  return (
    <div className="flex min-h-screen">
      {/* Left Side - Hero Section */}
      <div className="hidden lg:flex lg:w-1/2 bg-gradient-to-br from-teal-600 to-teal-800 relative overflow-hidden">
        <div className="absolute inset-0 opacity-20">
          <img
            src="https://lh3.googleusercontent.com/aida-public/AB6AXuAFvEs04e2UPv2R1fgmxFq_ExTlHWv7QpEHuhUZ41vZFnbAjbT8Lpyf5qcUPbbMU17DLdiM8Xt5a0yv692Pp6THia6xdgFVBm_vj-3_zmo1KFNL30bOXp94toyE1KgJv6nnezekjpwFWCRx2fUzRj4AcLd7P0n25Ut2Kojf33efE604pIFZOZ5XkD2cgpHS37uC8EA_XPuEL_uMKNasyFfLT8PS2Bky3CM7YfZPOo-SeZbKqbo8YPG94NWvB6TXlTtHq3LTIXO-Exv-"
            alt="Da Nang"
            className="w-full h-full object-cover"
          />
        </div>

        <div className="relative z-10 flex flex-col justify-between p-12 text-white w-full">
          {/* Logo */}
          <a href="/">
            <div className="flex items-center gap-2">
              <div className="w-10 h-10 bg-white rounded-lg flex items-center justify-center">
                <span className="text-teal-600 font-bold text-xl">L</span>
              </div>
              <span className="text-xl font-bold">
                LocalMate<span className="text-teal-200">SuperAgent</span>
              </span>
            </div>
          </a>

          {/* Hero Content */}
          <div className="max-w-lg">
            <div className="inline-block bg-white/20 backdrop-blur-sm px-4 py-2 rounded-full text-sm mb-6">
              Powered by LocalMate
            </div>

            <h1 className="text-5xl font-bold mb-6 leading-tight">
              Explore Da Nang
              <br />
              <span className="italic font-serif">Smarter & Deeper</span>
            </h1>

            <p className="text-lg text-white/90 leading-relaxed">
              Join thousands of tourists and drivers using our multimodal AI
              assistant for real-time planning and local insights.
            </p>
          </div>

          {/* Footer */}
          <div className="text-sm text-white/70">
            © 2024 Danang Tourism Super Agent • Privacy • Terms
          </div>
        </div>
      </div>

      {/* Right Side - Login Form */}
      <div className="w-full lg:w-1/2 flex items-center justify-center p-8 bg-gray-50">
        <div className="w-full max-w-md">
          {/* Mobile Logo */}
          <div className="lg:hidden flex items-center gap-2 mb-8">
            <div className="w-10 h-10 bg-gradient-to-br from-teal-500 to-teal-600 rounded-lg flex items-center justify-center">
              <span className="text-white font-bold text-xl">L</span>
            </div>
            <span className="text-xl font-bold">LocalMate</span>
          </div>

          <div className="mb-8">
            <Title order={1} className="text-3xl font-bold mb-2">
              Welcome back
            </Title>
            <Text c="dimmed" size="sm">
              Please enter your details to sign in.
            </Text>
          </div>

          {error && (
            <Alert
              icon={<IconAlertCircle size={16} />}
              color="red"
              variant="light"
              className="mb-6"
            >
              {error}
            </Alert>
          )}

          <Button
            onClick={handleGoogleLogin}
            disabled={loading}
            size="lg"
            radius="md"
            variant="outline"
            fullWidth
            leftSection={
              loading ? <Loader size="xs" /> : <IconBrandGoogle size={20} />
            }
            className="border-2 border-gray-200 hover:bg-gray-50 text-gray-700 mb-6"
          >
            {loading ? "Signing in..." : "Sign in with Google"}
          </Button>

          <Text size="xs" c="dimmed" ta="center" className="mt-8">
            Don't have an account?{" "}
            <Text component="span" c="teal" fw={600} className="cursor-pointer">
              Sign up for free
            </Text>
          </Text>
        </div>
      </div>
    </div>
  );
};

export default LoginPage;
