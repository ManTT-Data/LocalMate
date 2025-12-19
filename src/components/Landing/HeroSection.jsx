import React from "react";
import { Container, Title, Text, Button, Group, Box } from "@mantine/core";
import { useWindowScroll } from "@mantine/hooks";
import { useNavigate } from "react-router-dom";
import { IconPlane, IconCar } from "@tabler/icons-react";

const HeroSection = () => {
  const navigate = useNavigate();
  const [scroll] = useWindowScroll();

  const getParallaxOffset = (speed) => {
    return scroll.y * speed;
  };


  const heroImages = [
    {
      src: "https://lh3.googleusercontent.com/aida-public/AB6AXuAFvEs04e2UPv2R1fgmxFq_ExTlHWv7QpEHuhUZ41vZFnbAjbT8Lpyf5qcUPbbMU17DLdiM8Xt5a0yv692Pp6THia6xdgFVBm_vj-3_zmo1KFNL30bOXp94toyE1KgJv6nnezekjpwFWCRx2fUzRj4AcLd7P0n25Ut2Kojf33efE604pIFZOZ5XkD2cgpHS37uC8EA_XPuEL_uMKNasyFfLT8PS2Bky3CM7YfZPOo-SeZbKqbo8YPG94NWvB6TXlTtHq3LTIXO-Exv-",
      label: "Golden Bridge",
      delay: "0.2s",
    },
    {
      src: "https://lh3.googleusercontent.com/aida-public/AB6AXuAgs_cg5m1xAnRU7G_bCtaS5xWY8koDSV5sEVem9H1n4DVpgaN6wLWiLrerJaKb-LP9EMyWqvM6ZtnCj-YUk8TEcze4ZX_1_20tSRMtR61XizHa-f9EWct0YcUlt5zmqiG6f_SaXze8opYdETCZmhjCgpy0QF-0sE0dxqcA-ui4khUBUlC3NbvnhELT8FA1OSQEbsfELzNegiZLegTsKphYbK2LQ0V9T0tBNutvHJEuK9TahOR7Pe2-2C6lxIxFU9GFiyCSW5kLYhvN",
      label: "Dragon Bridge at Night",
      delay: "0",
    },
    {
      src: "https://lh3.googleusercontent.com/aida-public/AB6AXuBr0oVBCM55PSAdxUrqr-NhncLAQrgoK_urAAiTIMwPCx0slmXB_sufx3LTpdkZPw05J4daVTprbLhjy-yhw4bChEipJKB93MITk4v8TE1UJ3lESOOQn17zAKGvVFmmjgQGmgUFL4A8MeO3c1e0qx4fokl_VNU9b59W72El5zCNb9C4hk32Mmxi7kxvpKvuA_s5fYzNj5nychTMu_BTGOnVK_yFcx9SbHiLorxBZBrol6BGyKaBpOarjlkrhD5vvM3gPQBtt8kddIGx",
      label: "Hoi An Lanterns",
      delay: "0",
    },
    {
      src: "https://lh3.googleusercontent.com/aida-public/AB6AXuB0aM8AQK9lKQnje9WCBG7T5rNFycDJKhBZut2_cTxTo-Zbw9WHJszj26peMWBWOschuYOCw-ZNlNJ5LOxVLzJMIk0FZ202CjUwISTMnKd4p0RKHo9svE2TRencC-EydV4wLUPY_4bStMfabDmUHUFxg4HKZlAc-NhE75eCDn_rXr-qRbVR6Per6gx3k85T41gJJrc9r7K9H5WmknWmIoLMYTYov9w1lftpj3nOxZp-JU07ZSBQuU_mYn-v9i7GcoB-ovcXsScQP4Ws",
      label: "My Khe Beach",
      delay: "0.2s",
    },
  ];

  return (
    <Box className="relative pt-32 pb-20 lg:pt-48 lg:pb-32 overflow-hidden animated-mesh-bg">
      <Container size="xl" className="relative z-10">
        <div className="grid lg:grid-cols-2 gap-12 lg:gap-8 items-center">
          <div className="max-w-2xl animate-fadeIn">
            <div className="shimmer-badge inline-flex items-center space-x-2 bg-gradient-to-r from-teal-50 to-cyan-50 text-teal-600 px-4 py-2 rounded-full text-xs font-semibold mb-6 border border-teal-100">
              <span className="material-symbols-outlined text-sm">
                auto_awesome
              </span>
              <span>Powered by LocalMate team</span>
            </div>

            <Title
              order={1}
              className="text-5xl lg:text-7xl font-extrabold tracking-tight mb-6 leading-[1.1]"
            >
              Experience Da Nang <br />
              <span className="gradient-text font-serif italic pr-4">
                Smarter & Deeper
              </span>
            </Title>

            <Text
              size="lg"
              c="dimmed"
              className="mb-8 leading-relaxed max-w-lg"
            >
              The ultimate AI assistant for everyone in Da Nang. Whether you're
              a tourist seeking hidden gems or a Grab driver looking for local
              insights, our Super Agent guides you seamlessly.
            </Text>

            <Group gap="md" className="mb-10">
              <Button
                size="xl"
                radius="xl"
                className="btn-lift"
                leftSection={<IconPlane size={24} />}
                onClick={() => navigate("/login")}
                style={{
                  background: "linear-gradient(135deg, #00bfa6 0%, #0891B2 100%)",
                  border: "none",
                  boxShadow: "0 10px 30px -10px rgba(0, 191, 166, 0.5)",
                  paddingLeft: 32,
                  paddingRight: 32,
                  transition: "all 0.3s ease",
                }}
              >
                I'm a Tourist
              </Button>

              <Button
                size="xl"
                radius="xl"
                variant="default"
                className="btn-lift"
                leftSection={<IconCar size={24} />}
                onClick={() => navigate("/login")}
                style={{
                  background: "rgba(255, 255, 255, 0.9)",
                  backdropFilter: "blur(10px)",
                  border: "1px solid rgba(0, 0, 0, 0.08)",
                  color: "#171717",
                  boxShadow: "0 10px 30px -10px rgba(0, 0, 0, 0.15)",
                  paddingLeft: 32,
                  paddingRight: 32,
                  transition: "all 0.3s ease",
                }}
              >
                I'm a Driver
              </Button>
            </Group>

            <Group gap="sm" className="text-sm text-gray-500">
              <div className="flex -space-x-2">
                {[
                  "https://lh3.googleusercontent.com/aida-public/AB6AXuAvSEQZuMFK7qaQLMWXseuBolbh0MvW9azUVVpVb50tqZaExHizrYdDWGCGx9kbO6z6cIjTXreyeGENyAaur0tAUFvl61pyAmCZSCcbWVD9A68noK4j7fMmP8Z4klNefL7LaR1U_eOy7F3m9pCUKA6cRFY5-yQUMQ12iY_CG7FjjymMUhwErlVOHCsn58j98uadr1BmCA8LAxPpf4oosmsnr0hyirOP7NkgyBDETCrAkjpbGKZeOIXNE-ldiPRRBEAupVmXcxfh_ifA",
                  "https://lh3.googleusercontent.com/aida-public/AB6AXuBO4TLIj5R2zRc3yZoMCVn50yWhIelEZv1Ws7T619dFsT-Q7se0_vCMKXM8cQGTft2sTiICD9d_jCHxhkbpe9ophBgqrk_nzL9B-J5KH79DoHlOElvReCMTB-Zxau1BeB8-LP7-gPHy1SUh1jzySk4Me1cBZyJAbIuynQTNOcpfI0rZWz0UCG8k8i_Ypgdtq5HuFkmLLZwelP8Ef4SY5UzXFIABEA5hWRaZmh6OMg8dYlvrH9pJAy_5lQlXg8AmBky60ZVc9pSZ4SSo",
                  "https://lh3.googleusercontent.com/aida-public/AB6AXuD3ruOMFPkn1n_cEKr3JuK0IsBJs4bGsOH8ycyuGypyrp3knZYgqqcQ-_WivdD3PTXImN2bexSaaeS2_Tap0x_6AuuY-mtzLpFRQK8o3j0vOAhY1bS5sgouScPR0Tlp-maXnFYFSWxftOzLoLzO3rc3z4VKE5rtiXBNSA_OU-wV4SzY6-JPlxN2mjsdF8PZeBUPATqYNbE7cC-V8CeByO5XRk_HFIeVBj_KrXxgh7bqjycdVIvXh-IYsMq4xNwqyV4NSux_rBqg5W5d",
                ].map((src, i) => (
                  <img
                    key={i}
                    src={src}
                    alt={`User ${i + 1}`}
                    className="inline-block h-8 w-8 rounded-full ring-2 ring-white"
                  />
                ))}
              </div>
              <Text size="sm" c="dimmed">
                Trusted by 2,000+ travelers & locals
              </Text>
            </Group>
          </div>

          <div className="relative">
            <div className="grid grid-cols-2 gap-6">
              <div className="space-y-6">
                <Box
                  className="relative rounded-[32px] overflow-hidden shadow-2xl h-64 transform translate-y-12"
                  style={{
                    animation: `fadeIn 0.6s ease-out ${heroImages[0].delay}`,
                    boxShadow: "0 20px 40px -10px rgba(0,0,0,0.15)",
                    transform: `translateY(${48 + getParallaxOffset(-0.1)}px)`,
                  }}
                >
                  <img
                    src={heroImages[0].src}
                    alt={heroImages[0].label}
                    className="w-full h-full object-cover hover:scale-105 transition-transform duration-700"
                  />
                  <div className="absolute inset-0 bg-gradient-to-t from-black/60 to-transparent flex items-end p-6">
                    <Text size="sm" fw={600} c="white">
                      {heroImages[0].label}
                    </Text>
                  </div>
                </Box>
                <Box
                  className="relative rounded-[32px] overflow-hidden shadow-2xl h-48"
                  style={{
                    animation: `fadeIn 0.6s ease-out ${heroImages[1].delay}`,
                    boxShadow: "0 20px 40px -10px rgba(0,0,0,0.15)",
                    transform: `translateY(${getParallaxOffset(0.05)}px)`,
                  }}
                >
                  <img
                    src={heroImages[1].src}
                    alt={heroImages[1].label}
                    className="w-full h-full object-cover hover:scale-105 transition-transform duration-700"
                  />
                </Box>
              </div>

              <div className="space-y-6 pt-16">
                <Box
                  className="relative rounded-[32px] overflow-hidden shadow-2xl h-48"
                  style={{
                    animation: `fadeIn 0.6s ease-out ${heroImages[2].delay}`,
                    boxShadow: "0 20px 40px -10px rgba(0,0,0,0.15)",
                    transform: `translateY(${getParallaxOffset(-0.08)}px)`,
                  }}
                >
                  <img
                    src={heroImages[2].src}
                    alt={heroImages[2].label}
                    className="w-full h-full object-cover hover:scale-105 transition-transform duration-700"
                  />
                </Box>
                <Box
                  className="relative rounded-[32px] overflow-hidden shadow-2xl h-64"
                  style={{
                    animation: `fadeIn 0.6s ease-out ${heroImages[3].delay}`,
                    boxShadow: "0 20px 40px -10px rgba(0,0,0,0.15)",
                    transform: `translateY(${getParallaxOffset(0.12)}px)`,
                  }}
                >
                  <img
                    src={heroImages[3].src}
                    alt={heroImages[3].label}
                    className="w-full h-full object-cover hover:scale-105 transition-transform duration-700"
                  />
                  <div className="absolute inset-0 bg-gradient-to-t from-black/60 to-transparent flex items-end p-6">
                    <Text size="sm" fw={600} c="white">
                      {heroImages[3].label}
                    </Text>
                  </div>
                </Box>
              </div>
            </div>
          </div>
        </div>
      </Container>
    </Box>
  );
};

export default HeroSection;
