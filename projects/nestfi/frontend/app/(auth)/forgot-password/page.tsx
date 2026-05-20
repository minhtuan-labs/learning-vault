'use client';

import { useState } from 'react';

export default function ForgotPasswordPage() {
  const [email, setEmail] = useState('');
  const [submitted, setSubmitted] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    // TODO: Call reset-password endpoint
    setSubmitted(true);
  };

  return (
    <div>
      <h2 className="text-2xl font-semibold mb-6 text-center text-gray-900">
        Reset Password
      </h2>

      {submitted ? (
        <div className="space-y-4">
          <div className="p-4 bg-green-50 border border-green-200 rounded text-green-700 text-sm">
            If an account with that email exists, a reset link has been sent.
          </div>
          <p className="text-center text-gray-600">
            Check your email for further instructions.
          </p>
        </div>
      ) : (
        <form onSubmit={handleSubmit} className="space-y-4">
          <p className="text-gray-600 mb-6">
            Enter your email address and we&apos;ll send you a link to reset your password.
          </p>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Email
            </label>
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg text-gray-900 placeholder-gray-400"
              placeholder="you@example.com"
              required
            />
          </div>

          <button
            type="submit"
            className="w-full py-2 px-4 bg-blue-600 text-white font-medium rounded-lg hover:bg-blue-700"
          >
            Send Reset Link
          </button>

          <div className="text-center text-sm text-gray-600">
            <a href="/login" className="text-blue-600 hover:underline">
              Back to login
            </a>
          </div>
        </form>
      )}
    </div>
  );
}
