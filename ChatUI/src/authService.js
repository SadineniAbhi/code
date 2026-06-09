// AUTH DISABLED - All OTP-based authentication functions commented out
// const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;

// export const requestOTP = async (email) => {
//   try {
//     const response = await fetch(`${BACKEND_URL}/request-otp`, {
//       method: 'POST',
//       headers: {
//         'Content-Type': 'application/json',
//       },
//       body: JSON.stringify({ email }),
//     });

//     if (!response.ok) {
//       const error = await response.json();
//       throw new Error(error.detail || 'Failed to request OTP');
//     }

//     return await response.json();
//   } catch (error) {
//     console.error('Error requesting OTP:', error);
//     throw error;
//   }
// };

// export const verifyOTP = async (email, otp) => {
//   try {
//     const response = await fetch(`${BACKEND_URL}/verify-otp`, {
//       method: 'POST',
//       headers: {
//         'Content-Type': 'application/json',
//       },
//       body: JSON.stringify({ email, otp }),
//     });

//     if (!response.ok) {
//       const error = await response.json();
//       throw new Error(error.detail || 'Failed to verify OTP');
//     }

//     return await response.json();
//   } catch (error) {
//     console.error('Error verifying OTP:', error);
//     throw error;
//   }
// };

// export const makeAuthenticatedRequest = async (url, options = {}, token) => {
//   const headers = {
//     'Content-Type': 'application/json',
//     'Authorization': `Bearer ${token}`,
//     ...options.headers,
//   };

//   return fetch(url, {
//     ...options,
//     headers,
//   });
// };
