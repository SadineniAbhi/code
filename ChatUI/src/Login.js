// AUTH DISABLED - Login component completely commented out as auth is disabled
// import React, { useState } from 'react';
// import { requestOTP, verifyOTP } from './authService';
// import { useAuth } from './AuthContext';
// import './Login.css';

// const Login = () => {
//   const [step, setStep] = useState('email'); // 'email' or 'otp'
//   const [email, setEmail] = useState('');
//   const [otp, setOtp] = useState('');
//   const [loading, setLoading] = useState(false);
//   const [error, setError] = useState('');
//   const [message, setMessage] = useState('');

//   const { login } = useAuth();

//   const handleEmailSubmit = async (e) => {
//     e.preventDefault();
//     if (!email.trim()) return;

//     setLoading(true);
//     setError('');
//     setMessage('');

//     try {
//       await requestOTP(email);
//       setStep('otp');
//       setMessage('OTP sent to your email. Please check your inbox.');
//     } catch (err) {
//       setError(err.message || 'Failed to send OTP. Please try again.');
//     }

//     setLoading(false);
//   };

//   const handleOTPSubmit = async (e) => {
//     e.preventDefault();
//     if (!otp.trim()) return;

//     setLoading(true);
//     setError('');
//     setMessage('');

//     try {
//       const response = await verifyOTP(email, otp);
//       // Assuming the response contains a token field
//       if (response.token) {
//         login(response.token);
//       } else if (response.access_token) {
//         login(response.access_token);
//       } else {
//         // If no token field, create a simple token (you may need to adjust based on your backend response)
//         login('authenticated');
//       }
//     } catch (err) {
//       setError(err.message || 'Invalid OTP. Please try again.');
//     }

//     setLoading(false);
//   };

//   const handleBackToEmail = () => {
//     setStep('email');
//     setOtp('');
//     setError('');
//     setMessage('');
//   };

//   const handleResendOTP = async () => {
//     setLoading(true);
//     setError('');
//     setMessage('');

//     try {
//       await requestOTP(email);
//       setMessage('OTP resent to your email.');
//     } catch (err) {
//       setError(err.message || 'Failed to resend OTP.');
//     }

//     setLoading(false);
//   };

//   return (
//     <div className="login-container">
//       <div className="login-card">
//         <div className="login-header">
//           <img 
//             src="/assets/images/header-logo.png" 
//             alt="Header Logo" 
//             className="login-logo"
//             onError={(e) => {
//               e.target.style.display = 'none';
//               e.target.nextSibling.style.display = 'block';
//             }}
//           />
//           <h2 className="login-fallback" style={{display: 'none'}}>
//             Meil | Login
//           </h2>
//         </div>

//         {step === 'email' ? (
//           <form onSubmit={handleEmailSubmit} className="login-form">
//             <h2>Sign In</h2>
//             <p>Enter your email to receive an OTP</p>
            
//             <div className="form-group">
//               <label htmlFor="email">Email Address</label>
//               <input
//                 id="email"
//                 type="email"
//                 value={email}
//                 onChange={(e) => setEmail(e.target.value)}
//                 placeholder="Enter your email"
//                 required
//                 disabled={loading}
//               />
//             </div>

//             {error && <div className="error-message">{error}</div>}
//             {message && <div className="success-message">{message}</div>}

//             <button
//               type="submit"
//               disabled={loading || !email.trim()}
//               className="login-button"
//             >
//               {loading ? 'Sending...' : 'Send OTP'}
//             </button>
//           </form>
//         ) : (
//           <form onSubmit={handleOTPSubmit} className="login-form">
//             <h2>Verify OTP</h2>
//             <p>We've sent a 6-digit code to {email}</p>

//             <div className="form-group">
//               <label htmlFor="otp">Enter OTP</label>
//               <input
//                 id="otp"
//                 type="text"
//                 value={otp}
//                 onChange={(e) => setOtp(e.target.value.replace(/\D/g, '').slice(0, 6))}
//                 placeholder="000000"
//                 required
//                 disabled={loading}
//                 maxLength={6}
//               />
//             </div>

//             {error && <div className="error-message">{error}</div>}
//             {message && <div className="success-message">{message}</div>}

//             <button
//               type="submit"
//               disabled={loading || otp.length !== 6}
//               className="login-button"
//             >
//               {loading ? 'Verifying...' : 'Verify OTP'}
//             </button>

//             <div className="login-actions">
//               <button
//                 type="button"
//                 onClick={handleBackToEmail}
//                 className="back-button"
//                 disabled={loading}
//               >
//                 ← Back to Email
//               </button>
//               <button
//                 type="button"
//                 onClick={handleResendOTP}
//                 className="resend-button"
//                 disabled={loading}
//               >
//                 Resend OTP
//               </button>
//             </div>
//           </form>
//         )}
//       </div>
//     </div>
//   );
// };

// export default Login;

// Stub export to prevent import errors (since Login component is no longer used)
const Login = () => null;
export default Login;
