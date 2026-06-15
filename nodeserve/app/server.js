import express from 'express';
import { tasks } from './tasks.js';
import { inventory } from './inventory.js';

const server = express();
server.use(express.json());

server.get("/tasks", (req, res) => {
    res.json(tasks);
});

server.get("/inventory", (req, res) => {
    res.json(inventory);
});

server.post("/inventory", (req, res) => {
    const { name, quantity } = req.body;
    if (!name || !quantity) {
        return res.status(400).json({ error: "Name and quantity are required" });
    }
    const newItem = { uuid: crypto.randomUUID(), name, quantity };
    inventory.push(newItem);
    res.status(201).json(newItem);
});

server.put("/inventory:id", (req, res) => {
    const { id } = req.params;
    const { name, quantity } = req.body;
    const item = inventory.find(i => i.uuid === id);
    if (!item) {
        return res.status(404).json({ error: "Item not found" });
    }else{
        item.name = name || item.name;
        item.quantity = quantity || item.quantity;
        res.json(item);
    }
});


server.delete("/inventory:id", (req, res) => {
    const { id } = req.params;
    const index = inventory.findIndex(i => i.uuid === id);
    if (index === -1) {
        return res.status(404).json({ error: "Item not found" });
    }
    const deletedItem = inventory.splice(index, 1);
    res.json(deletedItem);
});

server.listen(3000, () => {
    console.log('Server is running on port 3000');
});