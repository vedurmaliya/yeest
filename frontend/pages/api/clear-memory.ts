import type { NextApiRequest, NextApiResponse } from 'next'
import axios from 'axios'

const BACKEND_URL = process.env.NEXT_PUBLIC_BACKEND_URL || 'http://127.0.0.1:8000'

export default async function handler(
  req: NextApiRequest,
  res: NextApiResponse
) {
  if (req.method !== 'POST') {
    return res.status(405).json({ error: 'Method not allowed' })
  }

  try {
    const response = await axios.post(`${BACKEND_URL}/clear-memory`, {}, {
      headers: {
        'Content-Type': 'application/json',
      },
      timeout: 10000,
    })

    res.status(200).json(response.data)
  } catch (error: any) {
    console.error('Error clearing memory:', error.message)
    
    if (error.response) {
      res.status(error.response.status).json({
        error: error.response.data?.detail || 'Backend error'
      })
    } else if (error.code === 'ECONNREFUSED') {
      res.status(503).json({
        error: 'Backend service is not available'
      })
    } else {
      res.status(500).json({
        error: 'Failed to clear memory'
      })
    }
  }
}
