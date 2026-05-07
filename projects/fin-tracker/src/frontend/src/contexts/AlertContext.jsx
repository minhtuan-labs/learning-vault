import { createContext, useContext, useState, useCallback } from "react";

const AlertContext = createContext(null);

export function AlertProvider({ children }) {
  const [unreadCount, setUnreadCount] = useState(0);
  const [refreshKey, setRefreshKey] = useState(0);

  const refreshAlerts = useCallback(() => {
    setRefreshKey((prev) => prev + 1);
  }, []);

  return (
    <AlertContext.Provider value={{ unreadCount, setUnreadCount, refreshAlerts, refreshKey }}>
      {children}
    </AlertContext.Provider>
  );
}

export function useAlerts() {
  const context = useContext(AlertContext);
  if (!context) {
    throw new Error("useAlerts must be used within AlertProvider");
  }
  return context;
}
