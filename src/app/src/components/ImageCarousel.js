import React from "react";
import { Box } from "@mui/material";
import Carousel from "react-material-ui-carousel";

const ImageCarousel = () => {
  const images = [
    { src: "https://via.placeholder.com/800x400", alt: "Financial Planning" },
    { src: "https://via.placeholder.com/800x400", alt: "Budgeting Tips" },
    { src: "https://via.placeholder.com/800x400", alt: "Investment.js Opportunities" },
  ];

  return (
    <Carousel>
      {images.map((image, index) => (
        <Box
          key={index}
          component="img"
          src={image.src}
          alt={image.alt}
          sx={{ width: "100%", borderRadius: "10px" }}
        />
      ))}
    </Carousel>
  );
};

export default ImageCarousel;
