import React from "react";
import { BrowserRouter } from "react-router-dom";
import Equipos from "./Equipos";

const EquiposPage: React.FC = () => {
  return (
    <BrowserRouter>
      <Equipos />
    </BrowserRouter>
  );
};

export default EquiposPage;
