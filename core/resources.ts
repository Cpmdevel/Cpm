// Resource System

class Resource {
    constructor(name, quantity) {
        this.name = name;
        this.quantity = quantity;
    }

    use(amount) {
        if (amount > this.quantity) {
            throw new Error('Not enough resources available.');
        }
        this.quantity -= amount;
    }

    replenish(amount) {
        this.quantity += amount;
    }
}

class ResourceSystem {
    constructor() {
        this.resources = {};
    }

    addResource(name, quantity) {
        this.resources[name] = new Resource(name, quantity);
    }

    useResource(name, amount) {
        const resource = this.resources[name];
        if (!resource) {
            throw new Error('Resource not found.');
        }
        resource.use(amount);
    }

    replenishResource(name, amount) {
        const resource = this.resources[name];
        if (!resource) {
            throw new Error('Resource not found.');
        }
        resource.replenish(amount);
    }

    getResource(name) {
        return this.resources[name];
    }
}

module.exports = ResourceSystem;