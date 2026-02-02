import { ChakraRootLayout } from '@/app/chakra_root_layout';
import type { Metadata } from 'next';

export const metadata: Metadata = {
  title: 'nebulapicker',
  icons: {
    icon: '/favicon.ico',
    apple: '/icons/icon-180.png',
  },
  appleWebApp: {
    capable: true,
    statusBarStyle: 'default',
  },
};

export default function RootLayout(
  { children }: { children: React.ReactNode }
) {
  return (
    <html lang="en" style={{ backgroundColor: '#1a202c' }}>
      <body
        style={
          { backgroundColor: 'black', color: 'white', minHeight: '100vh', margin: 0, padding: 0 }
        }
      >
        <ChakraRootLayout>
          {children}
        </ChakraRootLayout>
      </body>
    </html>
  );
}
