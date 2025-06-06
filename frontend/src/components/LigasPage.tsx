import React from "react";
import { BrowserRouter } from "react-router-dom";
import Ligas from "./Ligas";

const LigasPage: React.FC = () => {
  return (
    <BrowserRouter>
      <Ligas />
    </BrowserRouter>
  );
};

export default LigasPage;
