import ChatInterface from "@/components/ChatInterface";

export default function Home() {
  return (
    <main className="min-h-screen p-4 bg-gray-50">
      <div className="container mx-auto">
        <h1 className="text-3xl font-bold text-center mb-8">
          Mental Health Support Chat
        </h1>
        <ChatInterface />
      </div>
    </main>
  );
}
