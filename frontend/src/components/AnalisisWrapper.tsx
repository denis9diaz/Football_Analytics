import React from "react";
import { SuscripcionProvider } from "./SuscripcionContext";
import AnalisisComponent from "./Analisis";

export default function AnalisisWrapper() {
  return (
    <SuscripcionProvider>
      <div className="bg-white min-h-screen w-full">
        <main className="max-w-7xl mx-auto pt-8 px-4 py-10">
          <AnalisisComponent />
        </main>
      </div>
    </SuscripcionProvider>
  );
}
