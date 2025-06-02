import React from "react";

export default function Toast({ message }: { message: string }) {
  return (
    <div className="fixed top-6 left-1/2 transform -translate-x-1/2 z-50 bg-blue-600 text-white px-6 py-3 rounded shadow-lg animate__animated animate__fadeInDown">
      {message}
    </div>
  );
}
