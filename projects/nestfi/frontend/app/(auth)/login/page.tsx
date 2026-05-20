import LoginForm from '@/components/auth/LoginForm';

export default function LoginPage() {
  return (
    <div>
      <h2 className="text-2xl font-semibold mb-6 text-center text-gray-900">
        Welcome Back
      </h2>
      <LoginForm />
    </div>
  );
}
