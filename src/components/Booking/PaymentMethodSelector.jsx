import React, { useState } from "react";
import {
  Radio,
  Paper,
  Group,
  Stack,
  Text,
  Box,
  ActionIcon,
} from "@mantine/core";
import { IconPlus } from "@tabler/icons-react";

/**
 * Payment method selector component
 * Displays available payment methods with radio selection
 */
const PaymentMethodSelector = ({
  methods,
  selectedMethod,
  onSelect,
  onAddNew,
}) => {
  const [selected, setSelected] = useState(
    selectedMethod || methods.find((m) => m.isDefault)?.id
  );

  const handleSelect = (value) => {
    setSelected(value);
    onSelect?.(value);
  };

  return (
    <Stack gap="md">
      <Text size="xs" fw={700} c="dimmed" tt="uppercase">
        Payment Method
      </Text>

      <Radio.Group value={selected} onChange={handleSelect}>
        <Stack gap="sm">
          {methods.map((method) => (
            <Paper
              key={method.id}
              p="md"
              radius="lg"
              withBorder
              style={{
                borderWidth: 2,
                borderColor:
                  selected === method.id
                    ? "var(--mantine-color-blue-6)"
                    : "var(--mantine-color-gray-3)",
                backgroundColor:
                  selected === method.id
                    ? "var(--mantine-color-blue-0)"
                    : "transparent",
                cursor: "pointer",
                transition: "all 0.2s ease",
              }}
              onClick={() => handleSelect(method.id)}
            >
              <Group justify="space-between" wrap="nowrap">
                <Group gap="sm" style={{ flex: 1 }}>
                  <Box
                    w={20}
                    h={20}
                    style={{
                      borderRadius: "50%",
                      border: `2px solid ${
                        selected === method.id
                          ? "var(--mantine-color-blue-6)"
                          : "var(--mantine-color-gray-4)"
                      }`,
                      backgroundColor:
                        selected === method.id
                          ? "var(--mantine-color-blue-6)"
                          : "white",
                      display: "flex",
                      alignItems: "center",
                      justifyContent: "center",
                      flexShrink: 0,
                    }}
                  >
                    {selected === method.id && (
                      <Box
                        w={10}
                        h={10}
                        style={{
                          borderRadius: "50%",
                          backgroundColor: "white",
                        }}
                      />
                    )}
                  </Box>

                  <Group gap="sm" style={{ flex: 1 }}>
                    <Box
                      style={{
                        backgroundColor: method.color
                          ? `${method.color}15`
                          : "var(--mantine-color-gray-1)",
                        padding: "4px",
                        borderRadius: "4px",
                        display: "flex",
                        alignItems: "center",
                        justifyContent: "center",
                      }}
                    >
                      <span
                        className="material-symbols-outlined"
                        style={{
                          fontSize: 20,
                          color: method.color || "var(--mantine-color-gray-8)",
                        }}
                      >
                        {method.icon}
                      </span>
                    </Box>
                    <div>
                      <Text size="sm" fw={700}>
                        {method.name}
                      </Text>
                      <Text size="xs" c="dimmed">
                        {method.details}
                      </Text>
                    </div>
                  </Group>
                </Group>

                {selected === method.id && (
                  <span
                    className="material-symbols-outlined"
                    style={{
                      fontSize: 18,
                      color: "var(--mantine-color-gray-5)",
                    }}
                  >
                    check_circle
                  </span>
                )}
              </Group>
            </Paper>
          ))}
        </Stack>
      </Radio.Group>

      {/* Add new card button */}
      <Group gap="xs" style={{ cursor: "pointer" }} onClick={onAddNew}>
        <span
          className="material-symbols-outlined"
          style={{ fontSize: 14, color: "var(--mantine-color-blue-6)" }}
        >
          add
        </span>
        <Text size="xs" fw={700} c="blue" style={{ cursor: "pointer" }}>
          Add new card
        </Text>
      </Group>
    </Stack>
  );
};

export default PaymentMethodSelector;
