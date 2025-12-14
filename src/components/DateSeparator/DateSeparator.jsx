import React from "react";
import { Center, Badge } from "@mantine/core";

const DateSeparator = ({ date }) => {
  return (
    <Center>
      <Badge
        variant="light"
        color="gray"
        size="sm"
        radius="xl"
        styles={{
          root: {
            textTransform: "none",
          },
        }}
      >
        {date}
      </Badge>
    </Center>
  );
};

export default DateSeparator;
