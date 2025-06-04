import { useEffect, useState } from "react";

export default function AuthGuard({ children }: { children: React.ReactNode }) {
  const [isChecked, setIsChecked] = useState(false);

  useEffect(() => {
    const token = localStorage.getItem("access");
    if (!token) {
      window.location.href = "/login";
    } else {
      setIsChecked(true);
    }
  }, []);

  if (!isChecked) {
    return null;
  }

  return <>{children}</>;
}
