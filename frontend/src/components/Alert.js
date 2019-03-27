import React from 'react';
import { ToastContainer } from 'react-toastify';

export default React.memo(
  function Alert() {
    return <ToastContainer />;
  },
  (prevProps, nextProps) => true
);
