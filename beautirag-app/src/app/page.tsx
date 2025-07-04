'use client';

import React, { useState } from 'react';
import Image from "next/image";
import DocumentUpload from "@/components/DocumentUpload";
import ModelSelection from "@/components/ModelSelection";
import ChatInterface from "@/components/ChatInterface";

interface ValidatedConfig {
  model: string;
  apiKey: string;
}

export default function Home() {
  // State to hold the configuration after validation
  const [validatedConfig, setValidatedConfig] = useState<ValidatedConfig>({
    model: 'gpt-4o',
    apiKey: '',
  });

  const handleConfigValidated = (model: string, apiKey: string) => {
    console.log('Configuration validated in parent:', { model, apiKey });
    setValidatedConfig({ model, apiKey });
  };

  return (
    <main className="flex min-h-screen flex-col items-center p-12 md:p-20 lg:p-24 bg-gray-950 text-white">
      <div className="z-10 w-full max-w-6xl items-center justify-between font-mono text-sm lg:flex mb-12">
        <h1 className="text-4xl font-bold text-center w-full lg:text-5xl text-transparent bg-clip-text bg-gradient-to-r from-blue-400 to-purple-500 py-2">
          BeautiRAG App ✨
        </h1>
      </div>

      <div className="w-full max-w-7xl grid grid-cols-1 lg:grid-cols-3 gap-8 mb-0.5">
        <div className="lg:col-span-1 flex flex-col gap-8">
          <DocumentUpload />
          <ModelSelection
            onConfigValidated={handleConfigValidated}
            defaultModel={validatedConfig.model}
          />
        </div>

        <div className="lg:col-span-2">
          <ChatInterface
            selectedModel={validatedConfig.model}
            apiKey={validatedConfig.apiKey}
          />
        </div>
      </div>

      <footer className="w-full max-w-6xl text-center text-gray-500 text-sm mt-5">
        Built with Next.js, FastAPI, LangChain, by{" "}
        <span className="text-transparent bg-clip-text bg-gradient-to-r from-blue-400 to-purple-500">
          Zedems
        </span>
      </footer>
    </main>
  );
}
